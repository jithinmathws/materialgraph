from app.core.database import SessionLocal
from app.models.application import Application
from app.models.element import Element
from app.models.element_risk_profile import ElementRiskProfile


ELEMENTS = [
    {"symbol": "Li", "name": "Lithium", "atomic_number": 3, "category": "alkali metal"},
    {"symbol": "Na", "name": "Sodium", "atomic_number": 11, "category": "alkali metal"},
    {"symbol": "Mg", "name": "Magnesium", "atomic_number": 12, "category": "alkaline earth metal"},
    {"symbol": "Fe", "name": "Iron", "atomic_number": 26, "category": "transition metal"},
    {"symbol": "Mn", "name": "Manganese", "atomic_number": 25, "category": "transition metal"},
    {"symbol": "Co", "name": "Cobalt", "atomic_number": 27, "category": "transition metal"},
    {"symbol": "Ni", "name": "Nickel", "atomic_number": 28, "category": "transition metal"},
    {"symbol": "P", "name": "Phosphorus", "atomic_number": 15, "category": "nonmetal"},
    {"symbol": "O", "name": "Oxygen", "atomic_number": 8, "category": "nonmetal"},
]

APPLICATIONS = [
    {
        "name": "Battery Cathode",
        "description": "Candidate materials used as cathodes in battery systems.",
    },
    {
        "name": "Battery Anode",
        "description": "Candidate materials used as anodes in battery systems.",
    },
    {
        "name": "Solid Electrolyte",
        "description": "Candidate materials used as solid electrolytes in battery systems.",
    },
]

# Phase 1 normalized seed values.
# Scale convention:
# - abundance_score: higher is better
# - recyclability_score: higher is better
# - supply_risk_score: higher is worse
# - toxicity_score: higher is worse
# - geopolitical_risk_score: higher is worse
RISK_PROFILES = {
    "Li": {
        "abundance_score": 0.45,
        "supply_risk_score": 0.65,
        "toxicity_score": 0.25,
        "recyclability_score": 0.45,
        "geopolitical_risk_score": 0.55,
    },
    "Na": {
        "abundance_score": 0.90,
        "supply_risk_score": 0.15,
        "toxicity_score": 0.15,
        "recyclability_score": 0.50,
        "geopolitical_risk_score": 0.10,
    },
    "Mg": {
        "abundance_score": 0.80,
        "supply_risk_score": 0.20,
        "toxicity_score": 0.15,
        "recyclability_score": 0.55,
        "geopolitical_risk_score": 0.20,
    },
    "Fe": {
        "abundance_score": 0.85,
        "supply_risk_score": 0.20,
        "toxicity_score": 0.20,
        "recyclability_score": 0.75,
        "geopolitical_risk_score": 0.20,
    },
    "Mn": {
        "abundance_score": 0.65,
        "supply_risk_score": 0.45,
        "toxicity_score": 0.35,
        "recyclability_score": 0.50,
        "geopolitical_risk_score": 0.45,
    },
    "Co": {
        "abundance_score": 0.30,
        "supply_risk_score": 0.85,
        "toxicity_score": 0.65,
        "recyclability_score": 0.60,
        "geopolitical_risk_score": 0.90,
    },
    "Ni": {
        "abundance_score": 0.50,
        "supply_risk_score": 0.60,
        "toxicity_score": 0.45,
        "recyclability_score": 0.65,
        "geopolitical_risk_score": 0.60,
    },
    "P": {
        "abundance_score": 0.70,
        "supply_risk_score": 0.35,
        "toxicity_score": 0.25,
        "recyclability_score": 0.40,
        "geopolitical_risk_score": 0.30,
    },
    "O": {
        "abundance_score": 1.00,
        "supply_risk_score": 0.05,
        "toxicity_score": 0.05,
        "recyclability_score": 0.80,
        "geopolitical_risk_score": 0.05,
    },
}


def seed_elements(db):
    for item in ELEMENTS:
        existing = db.query(Element).filter(Element.symbol == item["symbol"]).first()

        if existing:
            continue

        db.add(Element(**item))


def seed_applications(db):
    for item in APPLICATIONS:
        existing = db.query(Application).filter(Application.name == item["name"]).first()

        if existing:
            continue

        db.add(Application(**item))


def seed_risk_profiles(db, year: int = 2026):
    elements = db.query(Element).all()
    element_by_symbol = {element.symbol: element for element in elements}

    for symbol, values in RISK_PROFILES.items():
        element = element_by_symbol.get(symbol)

        if element is None:
            continue

        existing = (
            db.query(ElementRiskProfile)
            .filter(
                ElementRiskProfile.element_id == element.id,
                ElementRiskProfile.year == year,
            )
            .first()
        )

        if existing:
            continue

        db.add(
            ElementRiskProfile(
                element_id=element.id,
                year=year,
                source="manual_phase_1_seed",
                **values,
            )
        )


def main():
    db = SessionLocal()

    try:
        seed_elements(db)
        seed_applications(db)
        db.commit()

        seed_risk_profiles(db)
        db.commit()

        print("Core seed data inserted successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()