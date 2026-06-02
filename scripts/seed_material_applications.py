# scripts/seed_material_applications.py

from app.core.database import SessionLocal
from app.models.application import Application
from app.models.material import Material
from app.models.material_application import MaterialApplication


APPLICATION_RULES = [
    {
        "application_name": "lithium-ion battery cathode",
        "formula_keywords": ["LiFePO4", "LiMn2O4", "LiMnO2"],
    },
    {
        "application_name": "sodium-ion battery cathode",
        "formula_keywords": ["NaFePO4", "Na3Fe", "NaFeP2O7", "NaMnO2"],
    },
    {
        "application_name": "phosphate cathode",
        "formula_keywords": ["PO4", "P2O7", "PO3"],
    },
    {
        "application_name": "manganese oxide cathode",
        "formula_keywords": ["MnO", "Mn2O4", "MnO2", "MnO3"],
    },
]


def get_or_create_application(db, name: str) -> Application:
    application = db.query(Application).filter(Application.name == name).first()

    if application is not None:
        return application

    application = Application(name=name)
    db.add(application)
    db.commit()
    db.refresh(application)

    return application


def main() -> None:
    db = SessionLocal()

    created_count = 0

    try:
        materials = db.query(Material).all()

        for rule in APPLICATION_RULES:
            application = get_or_create_application(db, rule["application_name"])

            for material in materials:
                formula = material.pretty_formula or material.formula

                if any(keyword in formula for keyword in rule["formula_keywords"]):
                    existing = (
                        db.query(MaterialApplication)
                        .filter(MaterialApplication.material_id == material.id)
                        .filter(MaterialApplication.application_id == application.id)
                        .first()
                    )

                    if existing is not None:
                        continue

                    material_application = MaterialApplication(
                        material_id=material.id,
                        application_id=application.id,
                        suitability_score=0.75,
                    )

                    db.add(material_application)
                    created_count += 1

        db.commit()

        print(f"Created material application mappings: {created_count}")

    finally:
        db.close()


if __name__ == "__main__":
    main()