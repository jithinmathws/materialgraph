from app.core.database import SessionLocal
from app.models.material import Material


def main() -> None:
    db = SessionLocal()

    try:
        deleted = (
            db.query(Material)
            .filter(Material.mp_id.like("mp-%test%"))
            .delete(synchronize_session=False)
        )

        db.commit()

        print(f"Deleted {deleted} test materials")

    finally:
        db.close()


if __name__ == "__main__":
    main()