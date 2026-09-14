import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CONTRACT_PATH = ROOT / "contracts" / "REDUCER_PRECEDENCE_v2.json"
FIXTURE_PATH = ROOT / "fixtures" / "REDUCER_CASES_v2.json"
RECEIPT_PATH = ROOT / "evidence" / "REDUCER_EXECUTION_v2.json"


class InputInvalid(ValueError):
    pass


class ContractInvalid(ValueError):
    pass


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)

    return h.hexdigest()


def canonical_sha256(value):
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


def validate_contract(contract):
    required = {
        "verification_states",
        "authority_states_ordered_most_to_least_permissive",
        "trusted_maximum_authority",
        "allowed_reason_classes",
        "precedence",
    }

    missing = required - set(contract)

    if missing:
        raise ContractInvalid(
            f"missing contract keys: {sorted(missing)}"
        )

    authority_states = (
        contract[
            "authority_states_ordered_most_to_least_permissive"
        ]
    )

    trusted_maximum = contract["trusted_maximum_authority"]

    if trusted_maximum not in authority_states:
        raise ContractInvalid(
            "trusted maximum authority is not in authority lattice"
        )

    ranks = [
        rule.get("rank")
        for rule in contract["precedence"]
    ]

    if len(ranks) != len(set(ranks)):
        raise ContractInvalid(
            "precedence ranks must be unique"
        )

    if sorted(ranks) != list(
        range(1, len(ranks) + 1)
    ):
        raise ContractInvalid(
            "precedence ranks must be contiguous"
        )

    for rule in contract["precedence"]:

        reason_classes = rule.get("reason_classes")

        if not isinstance(reason_classes, list):
            raise ContractInvalid(
                "rule reason_classes must be a list"
            )

        for reason in reason_classes:
            if reason not in contract[
                "allowed_reason_classes"
            ]:
                raise ContractInvalid(
                    f"unknown reason class in contract: {reason}"
                )

        verification_effect = rule.get(
            "verification_effect"
        )

        if verification_effect not in {
            "PRESERVE",
            "VERIFICATION_ERROR",
        }:
            raise ContractInvalid(
                "invalid verification effect"
            )

        authority_effect = rule.get(
            "authority_effect"
        )

        if (
            authority_effect is not None
            and authority_effect
            not in authority_states
        ):
            raise ContractInvalid(
                "invalid authority effect"
            )


def validate_case(case, contract):
    input_data = case.get("input")

    if not isinstance(input_data, dict):
        raise InputInvalid(
            "case input must be an object"
        )

    reason_classes = input_data.get(
        "reason_classes"
    )

    if not isinstance(reason_classes, list):
        raise InputInvalid(
            "reason_classes must be a list"
        )

    for reason in reason_classes:

        if not isinstance(reason, str):
            raise InputInvalid(
                "reason class must be a string"
            )

        if reason not in contract[
            "allowed_reason_classes"
        ]:
            raise InputInvalid(
                f"unknown reason class: {reason}"
            )

    verification_status = input_data.get(
        "verification_status_before_reducer"
    )

    if verification_status not in contract[
        "verification_states"
    ]:
        raise InputInvalid(
            "invalid verification status"
        )

    authority_state = input_data.get(
        "decision_authority_state_before_reducer"
    )

    if authority_state not in contract[
        "authority_states_ordered_most_to_least_permissive"
    ]:
        raise InputInvalid(
            "invalid authority state"
        )

    caller_ceiling = input_data.get(
        "authority_ceiling"
    )

    if (
        caller_ceiling is not None
        and caller_ceiling
        not in contract[
            "authority_states_ordered_most_to_least_permissive"
        ]
    ):
        raise InputInvalid(
            "invalid authority ceiling"
        )


def more_restrictive(
    authority_a,
    authority_b,
    ordered_states,
):
    """
    ordered_states:
    most permissive -> most restrictive
    """

    index_a = ordered_states.index(
        authority_a
    )

    index_b = ordered_states.index(
        authority_b
    )

    if index_a >= index_b:
        return authority_a

    return authority_b


def effective_cap(
    current_authority,
    trusted_maximum,
    caller_ceiling,
    ordered_states,
):
    """
    The canonical trusted maximum always applies.

    Caller input may further restrict authority,
    but can never widen it.
    """

    result = more_restrictive(
        current_authority,
        trusted_maximum,
        ordered_states,
    )

    if caller_ceiling is not None:
        result = more_restrictive(
            result,
            caller_ceiling,
            ordered_states,
        )

    return result


def reduce_case(case, contract):

    validate_contract(contract)
    validate_case(case, contract)

    input_data = case["input"]

    reasons = set(
        input_data["reason_classes"]
    )

    verification_status = input_data[
        "verification_status_before_reducer"
    ]

    current_authority = input_data[
        "decision_authority_state_before_reducer"
    ]

    caller_ceiling = input_data.get(
        "authority_ceiling"
    )

    ordered_states = contract[
        "authority_states_ordered_most_to_least_permissive"
    ]

    trusted_maximum = contract[
        "trusted_maximum_authority"
    ]

    capped_authority = effective_cap(
        current_authority,
        trusted_maximum,
        caller_ceiling,
        ordered_states,
    )

    rules = sorted(
        contract["precedence"],
        key=lambda rule: rule["rank"],
    )

    for rule in rules:

        rule_reasons = set(
            rule["reason_classes"]
        )

        if not reasons.intersection(
            rule_reasons
        ):
            continue

        verification_effect = rule[
            "verification_effect"
        ]

        if (
            verification_effect
            == "VERIFICATION_ERROR"
        ):
            return {
                "verification_status":
                    "VERIFICATION_ERROR",
                "decision_authority_state":
                    None,
            }

        candidate_authority = (
            rule["authority_effect"]
            if rule["authority_effect"]
            is not None
            else capped_authority
        )

        candidate_authority = (
            more_restrictive(
                candidate_authority,
                capped_authority,
                ordered_states,
            )
        )

        return {
            "verification_status":
                verification_status,
            "decision_authority_state":
                candidate_authority,
        }

    return {
        "verification_status":
            verification_status,
        "decision_authority_state":
            capped_authority,
    }


def build_receipt(
    fixtures,
    results,
):
    deterministic_payload = {
        "schema":
            "AICOS_REDUCER_EXECUTION_RESULT_v2",

        "inputs": {
            "runner_sha256":
                sha256_file(Path(__file__)),

            "fixture_sha256":
                sha256_file(FIXTURE_PATH),

            "precedence_contract_sha256":
                sha256_file(CONTRACT_PATH),
        },

        "result": {
            "total_cases":
                len(fixtures["cases"]),

            "passed_cases":
                sum(
                    1
                    for item in results
                    if item["status"] == "PASS"
                ),

            "failed_cases":
                sum(
                    1
                    for item in results
                    if item["status"] == "FAIL"
                ),
        },

        "case_results":
            results,
    }

    deterministic_payload[
        "result"
    ][
        "status"
    ] = (
        "PASS"
        if deterministic_payload[
            "result"
        ][
            "failed_cases"
        ] == 0
        else "FAIL"
    )

    receipt = {
        **deterministic_payload,

        "generated_at_utc":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "deterministic_result_sha256":
            canonical_sha256(
                deterministic_payload
            ),

        "environment": {
            "python_version":
                sys.version,

            "python_implementation":
                platform.python_implementation(),

            "platform":
                platform.platform(),

            "machine":
                platform.machine(),
        },

        "claim_boundary": {
            "established": [
                "FIRST_PARTY_IMPLEMENTATION",
                "FIRST_PARTY_ADVERSARIAL_TEST_EXECUTION",
                "TRUSTED_MAXIMUM_APPLIED_ON_TESTED_OUTPUT_PATHS",
                "VERIFICATION_NO_PROMOTION_ON_TESTED_ADVERSE_AUTHORITY_EVENTS",
                "HASH_BOUND_DETERMINISTIC_SEMANTIC_RESULT"
            ],

            "not_established": [
                "EXTERNAL_REPRODUCTION",
                "INDEPENDENT_TECHNICAL_EVALUATION",
                "INDEPENDENT_VALIDATION",
                "PRODUCTION_OPERATION"
            ]
        }
    }

    return receipt


def main():

    contract = load_json(
        CONTRACT_PATH
    )

    fixtures = load_json(
        FIXTURE_PATH
    )

    results = []

    for case in fixtures["cases"]:

        case_id = case["id"]

        try:

            actual = reduce_case(
                case,
                contract,
            )

            expected = case.get(
                "expected"
            )

            if actual == expected:
                status = "PASS"
            else:
                status = "FAIL"

            result = {
                "id": case_id,
                "status": status,
                "actual": actual,
                "expected": expected,
            }

        except (
            InputInvalid,
            ContractInvalid,
        ) as error:

            expected_error = case.get(
                "expected_error"
            )

            actual_error = (
                type(error).__name__
            )

            if (
                expected_error
                == actual_error
            ):
                status = "PASS"
            else:
                status = "FAIL"

            result = {
                "id": case_id,
                "status": status,
                "actual": {
                    "error":
                        actual_error,
                    "message":
                        str(error),
                },
                "expected_error":
                    expected_error,
            }

        results.append(result)

        print(
            result["status"],
            case_id,
            result.get("actual"),
        )

    receipt = build_receipt(
        fixtures,
        results,
    )

    RECEIPT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RECEIPT_PATH.write_text(
        json.dumps(
            receipt,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(
        "TOTAL:",
        receipt["result"]["total_cases"],
    )

    print(
        "PASSED:",
        receipt["result"]["passed_cases"],
    )

    print(
        "FAILED:",
        receipt["result"]["failed_cases"],
    )

    print(
        "STATUS:",
        receipt["result"]["status"],
    )

    print(
        "DETERMINISTIC_RESULT_SHA256:",
        receipt[
            "deterministic_result_sha256"
        ],
    )

    if (
        receipt["result"]["failed_cases"]
        != 0
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
