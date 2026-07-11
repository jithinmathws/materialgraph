import json
from typing import Any

from sqlalchemy import text

from app.core.database import SessionLocal


def describe_value(value: Any) -> str:
    if isinstance(value, dict):
        return f"dict with {len(value)} keys"
    if isinstance(value, list):
        return f"list with {len(value)} items"
    return f"{type(value).__name__}: {value!r}"


def main() -> None:
    db = SessionLocal()

    try:
        result = db.execute(
            text(
                """
                SELECT
                    id,
                    mp_id,
                    formula,
                    pretty_formula,
                    raw_data
                FROM materials
                WHERE id IN (:lifepo4_id)
                   OR formula IN ('LiFePO4', 'NaFePO4')
                ORDER BY id
                LIMIT 5;
                """
            ),
            {"lifepo4_id": 5},
        )

        materials = result.mappings().all()

        if not materials:
            print("No matching materials found.")
            return

        for material in materials:
            print("\n" + "=" * 80)
            print(
                f"id={material['id']} "
                f"mp_id={material['mp_id']} "
                f"formula={material['formula']} "
                f"pretty_formula={material['pretty_formula']}"
            )

            raw_data = material["raw_data"]

            if raw_data is None:
                print("raw_data: None")
                continue

            # PostgreSQL JSON may already be returned as a dict.
            if isinstance(raw_data, str):
                raw_data = json.loads(raw_data)

            if not isinstance(raw_data, dict):
                print(f"Unexpected raw_data type: {type(raw_data).__name__}")
                print(raw_data)
                continue

            print("\nTop-level raw_data keys:")
            for key in sorted(raw_data):
                print(f"- {key}: {describe_value(raw_data[key])}")

            print("\nLikely composition-related fields:")
            for key in (
                "composition",
                "composition_reduced",
                "formula_pretty",
                "formula_anonymous",
                "chemsys",
                "elements",
                "nelements",
            ):
                if key in raw_data:
                    print(f"\n{key}:")
                    print(
                        json.dumps(
                            raw_data[key],
                            indent=2,
                            default=str,
                        )
                    )

    except Exception as exc:
        print(f"Inspection failed: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()