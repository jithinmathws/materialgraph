from app.core.config import settings
from app.core.database import SessionLocal
from app.services.material_import_service import MaterialImportService
from app.services.materials_project_service import MaterialsProjectService


BATTERY_CHEMICAL_SYSTEMS = [
    "Li-Fe-P-O",
    "Na-Fe-P-O",
    "Na-Mn-O",
    "Mg-Mn-O",
    "Li-Mn-O",
]


def main() -> None:
    if not settings.materials_project_api_key:
        raise ValueError(
            "materials_project_api_key is not configured"
        )

    mp_service = MaterialsProjectService(
        api_key=settings.materials_project_api_key,
    )

    db = SessionLocal()

    try:
        importer = MaterialImportService(db)

        total_imported = 0

        for chemsys in BATTERY_CHEMICAL_SYSTEMS:
            print(f"\nFetching {chemsys} ...")

            candidates = mp_service.fetch_materials(
                chemsys=chemsys,
                limit=25,
            )

            imported = importer.import_materials(
                candidates
            )

            total_imported += imported

            print(
                f"{chemsys}: "
                f"{len(candidates)} fetched, "
                f"{imported} imported"
            )

        print(
            f"\nCompleted. "
            f"Total imported: {total_imported}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()