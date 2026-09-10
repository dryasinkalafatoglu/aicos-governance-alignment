import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FIXTURE_PATH = ROOT / "fixtures" / "REDUCER_CASES.json"
PRECEDENCE_PATH = ROOT / "contracts" / "REDUCER_PRECEDENCE.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


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


def main():
    fixtures = load_json(FIXTURE_PATH)
    precedence = load_json(PRECEDENCE_PATH)

    total = 0
    passed = 0

    for case in fixtures["cases"]:
        total += 1

        actual = reduce_case(case, precedence)
        expected = case["expected"]

        if actual == expected:
            passed += 1
            print(f"PASS {case['id']}")
        else:
            print(f"FAIL {case['id']}")
            print(f"  expected: {expected}")
            print(f"  actual:   {actual}")

    print()
    print(f"RESULT {passed}/{total} PASS")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
