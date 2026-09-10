import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FIXTURE_PATH = ROOT / "fixtures" / "REDUCER_CASES.json"
PRECEDENCE_PATH = ROOT / "contracts" / "REDUCER_PRECEDENCE.json"
RECEIPT_PATH = ROOT / "evidence" / "REDUCER_EXECUTION_LATEST.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()


def reduce_case(case, precedence):
    inputs = case["input"]

    reason_classes = set(inputs.get("reason_classes", []))
    verification_status = inputs.get("verification_status_before_reducer")
    authority_state = inputs.get("decision_authority_state_before_reducer")
    authority_ceiling = inputs.get("authority_ceiling")

    for rule in sorted(precedence["precedence"], key=lambda x: x["rank"]):
        condition = rule["condition"]

        if condition == "VERIFICATION_INTEGRITY_BROKEN":
            if reason_classes.intersection(
                {"STRUCTURAL_ERROR", "INTERNAL_VERIFICATION_ERROR"}
            ):
                effect = rule["terminal_effect"]
                return {
                    "verification_status": effect["verification_status"],
                    "decision_authority_state": effect["decision_authority_state"],
                }

        elif condition == "MANDATORY_KNOWN_VIOLATION":
            if "KNOWN_VIOLATION" in reason_classes:
                effect = rule["terminal_effect"]
                return {
                    "verification_status": effect["verification_status"],
                    "decision_authority_state": effect["decision_authority_state"],
                }

        elif condition == "EPISTEMIC_UNKNOWN":
            if "EPISTEMIC_UNKNOWN" in reason_classes:
                effect = rule["terminal_effect"]
                return {
                    "verification_status": effect["verification_status"],
                    "decision_authority_state": effect["decision_authority_state"],
                }

        elif condition == "OPERATIONAL_HOLD":
            if "OPERATIONAL_HOLD" in reason_classes:
                effect = rule["terminal_effect"]
                return {
                    "verification_status": effect["verification_status"],
                    "decision_authority_state": effect["decision_authority_state"],
                }

        elif condition == "AUTHORITY_CEILING":
            if authority_ceiling is not None:
                return {
                    "verification_status": verification_status,
                    "decision_authority_state": authority_ceiling,
                }

    return {
        "verification_status": verification_status,
        "decision_authority_state": authority_state,
    }


def build_receipt(case_results, total, passed):
    return {
        "schema": "AICOS_REDUCER_EXECUTION_RECEIPT_v1",
        "execution_type": "FIRST_PARTY_EXECUTION",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "runner": {
                "path": "tools/run_reducer_cases.py",
                "sha256": sha256_file(Path(__file__)),
            },
            "fixture": {
                "path": "fixtures/REDUCER_CASES.json",
                "sha256": sha256_file(FIXTURE_PATH),
            },
            "precedence_contract": {
                "path": "contracts/REDUCER_PRECEDENCE.json",
                "sha256": sha256_file(PRECEDENCE_PATH),
            },
        },
        "result": {
            "total_cases": total,
            "passed_cases": passed,
            "failed_cases": total - passed,
            "exit_code": 0 if passed == total else 1,
            "status": "PASS" if passed == total else "FAIL",
        },
        "case_results": case_results,
        "claim_boundary": {
            "established": [
                "FIRST_PARTY_EXECUTION",
                "DETERMINISTIC_FIXTURE_EXECUTION",
                "HASH_BOUND_EXECUTION_RECEIPT",
            ],
            "not_established": [
                "EVIDENCE_TRUTH",
                "EXTERNAL_REPRODUCTION",
                "EXTERNAL_TECHNICAL_REVIEW",
                "INDEPENDENT_EVALUATION",
                "INDEPENDENT_VALIDATION",
                "PRODUCTION_OPERATION",
            ],
        },
        "governing_rules": [
            "ClaimStrength <= EvidenceStrength",
            "DeterministicReceipt != EvidenceTruth",
        ],
    }


def write_receipt(receipt):
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with RECEIPT_PATH.open("w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, sort_keys=True)
        f.write("\n")


def main():
    fixtures = load_json(FIXTURE_PATH)
    precedence = load_json(PRECEDENCE_PATH)

    total = 0
    passed = 0
    case_results = []

    for case in fixtures["cases"]:
        total += 1

        actual = reduce_case(case, precedence)
        expected = case["expected"]

        status = "PASS" if actual == expected else "FAIL"

        if status == "PASS":
            passed += 1

        case_results.append(
            {
                "id": case["id"],
                "status": status,
                "expected": expected,
                "actual": actual,
            }
        )

        print(f"{status} {case['id']}")

        if status == "FAIL":
            print(f"  expected: {expected}")
            print(f"  actual:   {actual}")

    receipt = build_receipt(case_results, total, passed)
    write_receipt(receipt)

    print()
    print(f"RESULT {passed}/{total} PASS")
    print(f"RECEIPT {RECEIPT_PATH.relative_to(ROOT)}")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
