from fastapi import APIRouter

from app.api.v1.routes.applications import router as applications_router
from app.api.v1.routes.elements import router as elements_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.materials import router as materials_router
from app.api.v1.routes.risks import router as risks_router
from app.api.v1.routes.screening import router as screening_router
from app.api.v1.routes.material_risks import router as material_risks_router
from app.api.v1.routes.comparison import router as comparison_router
from app.api.v1.routes.scenario_ranking import router as scenario_ranking_router
from app.api.v1.routes.sensitivity import router as sensitivity_router
from app.api.v1.routes.substitutions import router as substitutions_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(materials_router)
api_router.include_router(elements_router)
api_router.include_router(applications_router)
api_router.include_router(risks_router)
api_router.include_router(screening_router)
api_router.include_router(material_risks_router)
api_router.include_router(comparison_router)
api_router.include_router(scenario_ranking_router)
api_router.include_router(sensitivity_router)
api_router.include_router(substitutions_router)