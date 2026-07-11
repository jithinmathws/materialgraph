import json

from sqlalchemy import text

from app.core.database import SessionLocal


def load_json(value):
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        return json.loads(value)
    return None


def main():
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT
                    id,
                    mp_id,
                    formula,
                    raw_data
                FROM materials
                ORDER BY id;
            """)
        ).mappings().all()

        total = len(rows)

        with_composition = 0
        without_composition = 0

        raw_id_matches = 0
        raw_id_mismatches = 0
        raw_id_missing = 0

        mp_test = 0

        missing_examples = []
        mismatch_examples = []

        for row in rows:
            raw = load_json(row["raw_data"])

            if row["mp_id"].startswith("mp-test"):
                mp_test += 1

            if raw is None:
                without_composition += 1
                continue

            composition = raw.get("composition")

            if composition:
                with_composition += 1
            else:
                without_composition += 1

                if len(missing_examples) < 10:
                    missing_examples.append(
                        (
                            row["id"],
                            row["mp_id"],
                            row["formula"],
                        )
                    )

            raw_material_id = raw.get("material_id")

            if raw_material_id is None:
                raw_id_missing += 1

            elif raw_material_id == row["mp_id"]:
                raw_id_matches += 1

            else:
                raw_id_mismatches += 1

                if len(mismatch_examples) < 10:
                    mismatch_examples.append(
                        (
                            row["id"],
                            row["mp_id"],
                            raw_material_id,
                        )
                    )

        print("=" * 70)
        print("Material Composition Coverage Audit")
        print("=" * 70)

        print(f"Total materials                : {total}")
        print(f"With composition              : {with_composition}")
        print(f"Without composition           : {without_composition}")
        print()

        print(f"Test materials (mp-test)      : {mp_test}")
        print()

        print(f"raw_data.material_id matches  : {raw_id_matches}")
        print(f"raw_data.material_id mismatch : {raw_id_mismatches}")
        print(f"raw_data.material_id missing  : {raw_id_missing}")

        print("\nMaterials missing composition")

        for item in missing_examples:
            print(item)

        print("\nIdentifier mismatches")

        for item in mismatch_examples:
            print(item)

    finally:
        db.close()


if __name__ == "__main__":
    main()