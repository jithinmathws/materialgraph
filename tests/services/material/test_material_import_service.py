import pytest
from uuid import uuid4

from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.material.import_service import MaterialImportService
from app.services.material.project_service import MaterialCandidate


def make_candidate(
    mp_id: str | None = None,
    formula: str = "LiFePO4",
    pretty_formula: str = "LiFePO4",
    elements: list[str] | None = None,
    composition_fractions: dict[str, float] | None = None,
) -> MaterialCandidate:
    generated_mp_id = mp_id or f"mp-test-{uuid4()}"
    candidate_elements = elements or ["Li", "Fe", "P", "O"]

    if composition_fractions is None:
        composition_fractions = {
            "Li": 1 / 7,
            "Fe": 1 / 7,
            "P": 1 / 7,
            "O": 4 / 7,
        }

    return MaterialCandidate(
        mp_id=generated_mp_id,
        formula=formula,
        pretty_formula=pretty_formula,
        elements=candidate_elements,
        band_gap=1.2,
        energy_above_hull=0.0,
        formation_energy_per_atom=-2.5,
        density=3.6,
        is_stable=True,
        raw_data={
            "material_id": generated_mp_id,
            "formula_pretty": pretty_formula,
            "composition": {
                symbol: fraction
                for symbol, fraction in composition_fractions.items()
            },
        },
        composition_fractions=composition_fractions,
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

    elements_by_id = {
        element.id: element.symbol
        for element in db_session.query(Element).all()
    }

    fractions_by_symbol = {
        elements_by_id[link.element_id]: link.fraction
        for link in links
    }

    assert len(links) == 4

    assert fractions_by_symbol == pytest.approx(
        {
            "Li": 1 / 7,
            "Fe": 1 / 7,
            "P": 1 / 7,
            "O": 4 / 7,
        }
    )

    assert sum(fractions_by_symbol.values()) == pytest.approx(1.0)


def test_import_materials_preserves_legacy_fraction_fallback(db_session):
    service = MaterialImportService(db_session)

    candidate = make_candidate(
        composition_fractions={},
    )

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


def test_import_materials_rejects_missing_composition_element(db_session):
    service = MaterialImportService(db_session)

    candidate = make_candidate(
        composition_fractions={
            "Li": 0.2,
            "Fe": 0.2,
            "P": 0.2,
        }
    )

    with pytest.raises(
        ValueError,
        match="element membership does not match",
    ):
        service.import_materials([candidate])


def test_import_materials_rejects_unexpected_composition_element(db_session):
    service = MaterialImportService(db_session)

    candidate = make_candidate(
        composition_fractions={
            "Li": 0.1,
            "Fe": 0.1,
            "P": 0.1,
            "O": 0.6,
            "Na": 0.1,
        }
    )

    with pytest.raises(
        ValueError,
        match="element membership does not match",
    ):
        service.import_materials([candidate])


@pytest.mark.parametrize(
    "invalid_fraction",
    [
        0.0,
        -0.1,
        float("nan"),
        float("inf"),
    ],
)
def test_import_materials_rejects_invalid_fraction(
    db_session,
    invalid_fraction: float,
):
    service = MaterialImportService(db_session)

    candidate = make_candidate(
        composition_fractions={
            "Li": invalid_fraction,
            "Fe": 1.0,
            "P": 1.0,
            "O": 4.0,
        }
    )

    with pytest.raises(
        ValueError,
        match="invalid composition fraction",
    ):
        service.import_materials([candidate])