from uuid import uuid4

from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.material_import_service import MaterialImportService
from app.services.materials_project_service import MaterialCandidate


def make_candidate(
    mp_id: str | None = None,
    formula: str = "LiFePO4",
    pretty_formula: str = "LiFePO4",
    elements: list[str] | None = None,
) -> MaterialCandidate:
    generated_mp_id = mp_id or f"mp-test-{uuid4()}"

    return MaterialCandidate(
        mp_id=generated_mp_id,
        formula=formula,
        pretty_formula=pretty_formula,
        elements=elements or ["Li", "Fe", "P", "O"],
        band_gap=1.2,
        energy_above_hull=0.0,
        formation_energy_per_atom=-2.5,
        density=3.6,
        is_stable=True,
        raw_data={
            "material_id": generated_mp_id,
            "formula_pretty": pretty_formula,
        },
    )


def test_import_materials_creates_material(db_session):
    service = MaterialImportService(db_session)
    candidate = make_candidate()

    imported_count = service.import_materials([candidate])

    material = (
        db_session.query(Material)
        .filter(Material.mp_id == candidate.mp_id)
        .first()
    )

    assert imported_count == 1
    assert material is not None
    assert material.pretty_formula == "LiFePO4"
    assert material.source == "materials_project"
    assert material.is_stable is True
    assert material.raw_data["material_id"] == candidate.mp_id


def test_import_materials_skips_duplicate_mp_id(db_session):
    service = MaterialImportService(db_session)
    candidate = make_candidate()

    first_count = service.import_materials([candidate])
    second_count = service.import_materials([candidate])

    material_count = (
        db_session.query(Material)
        .filter(Material.mp_id == candidate.mp_id)
        .count()
    )

    assert first_count == 1
    assert second_count == 0
    assert material_count == 1


def test_import_materials_creates_elements(db_session):
    service = MaterialImportService(db_session)
    candidate = make_candidate()

    service.import_materials([candidate])

    symbols = {
        element.symbol
        for element in db_session.query(Element).all()
    }

    assert {"Li", "Fe", "P", "O"}.issubset(symbols)


def test_import_materials_creates_material_element_links(db_session):
    service = MaterialImportService(db_session)
    candidate = make_candidate()

    service.import_materials([candidate])

    material = (
        db_session.query(Material)
        .filter(Material.mp_id == candidate.mp_id)
        .one()
    )

    links = (
        db_session.query(MaterialElement)
        .filter(MaterialElement.material_id == material.id)
        .all()
    )

    assert len(links) == 4
    assert all(link.fraction == 1.0 for link in links)