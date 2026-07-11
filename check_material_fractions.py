from sqlalchemy import text

from app.core.database import SessionLocal


def main() -> None:
    db = SessionLocal()

    try:
        print("\nFraction distribution")
        print("-" * 40)

        result = db.execute(
            text(
                """
                SELECT
                    fraction,
                    COUNT(*) AS row_count
                FROM material_elements
                GROUP BY fraction
                ORDER BY fraction;
                """
            )
        )

        for row in result:
            print(f"fraction={row.fraction}, rows={row.row_count}")

        print("\nLiFePO4 fractions — material_id 5")
        print("-" * 40)

        result = db.execute(
            text(
                """
                SELECT
                    e.symbol,
                    me.fraction
                FROM material_elements AS me
                JOIN elements AS e
                    ON e.id = me.element_id
                WHERE me.material_id = :material_id
                ORDER BY e.symbol;
                """
            ),
            {"material_id": 5},
        )

        rows = result.all()

        if not rows:
            print("No material-element rows found for material_id=5.")
        else:
            for row in rows:
                print(f"{row.symbol}: {row.fraction}")

    except Exception as exc:
        print(f"Database inspection failed: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()