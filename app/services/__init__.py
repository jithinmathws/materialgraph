def __init__(self, db: Session):
    self.db = db
    self.weights = DEFAULT_SCREENING_WEIGHTS
    self.material_risk_service = MaterialRiskService(db)