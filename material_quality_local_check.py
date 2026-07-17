from app.core.database import SessionLocal
from app.services.material.quality_service import MaterialQualityService


db = SessionLocal()

try:
    service = MaterialQualityService(db)

    for material_id in [5, 6, 7, 8, 9, 10]:
        quality = service.get_material_quality(material_id)

        print(
            material_id,
            {
                "risk_score": quality["risk_score"],
                "risk_known": quality["risk_known"],
                "risk_profile_coverage": quality["risk_profile_coverage"],
                "known_risk_element_count": quality["known_risk_element_count"],
                "total_element_count": quality["total_element_count"],
                "risk_evidence_complete": quality["risk_evidence_complete"],
                "unknown_risk_elements": quality["unknown_risk_elements"],
                "quality_score": quality["quality_score"],
            },
        )
finally:
    db.close()