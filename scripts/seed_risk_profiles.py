from app.core.database import SessionLocal
from app.models.element import Element
from app.models.element_risk_profile import ElementRiskProfile


YEAR = 2026

RISK_DATA = {
    "Li": {
        "abundance_score": 4,
        "supply_risk_score": 8,
        "toxicity_score": 2,
        "recyclability_score": 6,
        "geopolitical_risk_score": 8,
    },
    "Co": {
        "abundance_score": 2,
        "supply_risk_score": 10,
        "toxicity_score": 8,
        "recyclability_score": 6,
        "geopolitical_risk_score": 10,
    },
    "Na": {
        "abundance_score": 9,
        "supply_risk_score": 1,
        "toxicity_score": 1,
        "recyclability_score": 7,
        "geopolitical_risk_score": 1,
    },
    "Mg": {
        "abundance_score": 8,
        "supply_risk_score": 2,
        "toxicity_score": 1,
        "recyclability_score": 7,
        "geopolitical_risk_score": 2,
    },
    "Fe": {
        "abundance_score": 9,
        "supply_risk_score": 1,
        "toxicity_score": 1,
        "recyclability_score": 9,
        "geopolitical_risk_score": 1,
    },
    "Mn": {
        "abundance_score": 7,
        "supply_risk_score": 3,
        "toxicity_score": 3,
        "recyclability_score": 7,
        "geopolitical_risk_score": 3,
    },
    "P": {
        "abundance_score": 6,
        "supply_risk_score": 4,
        "toxicity_score": 2,
        "recyclability_score": 5,
        "geopolitical_risk_score": 4,
    },
    "O": {
        "abundance_score": 10,
        "supply_risk_score": 1,
        "toxicity_score": 1,
        "recyclability_score": 10,
        "geopolitical_risk_score": 1,
    },
    "F": {
        "abundance_score": 5,
        "supply_risk_score": 5,
        "toxicity_score": 7,
        "recyclability_score": 4,
        "geopolitical_risk_score": 5,
    },
}


def main() -> None:
    db = SessionLocal()

    try:
        created = 0
        updated = 0

        for symbol, scores in RISK_DATA.items():
            element = db.query(Element).filter(Element.symbol == symbol).first()

            if element is None:
                print(f"Skipping {symbol}: element not found")
                continue

            profile = (
                db.query(ElementRiskProfile)
                .filter(
                    ElementRiskProfile.element_id == element.id,
                    ElementRiskProfile.year == YEAR,
                )
                .first()
            )

            if profile is None:
                profile = ElementRiskProfile(
                    element_id=element.id,
                    year=YEAR,
                    source="manual_phase_1_seed",
                    **scores,
                )
                db.add(profile)
                created += 1
            else:
                for field, value in scores.items():
                    setattr(profile, field, value)
                profile.source = "manual_phase_1_seed"
                updated += 1

        db.commit()

        print(f"Created: {created}")
        print(f"Updated: {updated}")

    finally:
        db.close()


if __name__ == "__main__":
    main()