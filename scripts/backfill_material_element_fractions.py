from __future__ import annotations

import argparse
from dataclasses import dataclass
from math import isclose
from typing import Any

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.material.composition_service import (
    MaterialCompositionService,
)


FRACTION_SUM_ABS_TOLERANCE = 1e-9


@dataclass
class BackfillSummary:
    discovered: int = 0
    eligible: int = 0
    updated_materials: int = 0
    updated_links: int = 0
    unchanged_materials: int = 0
    skipped_test_materials: int = 0
    skipped_missing_composition: int = 0
    failed_materials: int = 0


@dataclass(frozen=True)
class MaterialBackfillResult:
    material_id: int
    mp_id: str
    formula: str
    changed_links: int
    previous_fractions: dict[str, float]
    corrected_fractions: dict[str, float]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Backfill normalized MaterialElement fractions from structured "
            "Materials Project composition data."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Commit corrected fractions. Without this option, the script "
            "runs in dry-run mode and rolls back all changes."
        ),
    )

    parser.add_argument(
        "--mp-id",
        type=str,
        default=None,
        help=(
            "Process one Materials Project material only, for example "
            "'mp-19017'."
        ),
    )

    return parser.parse_args()


def extract_composition_amounts(
    raw_data: dict[str, Any] | None,
) -> dict[str, float] | None:
    """
    Extract a direct element-to-amount mapping from stored MP raw data.

    Expected form:

        {
            "composition": {
                "Li": 1.0,
                "Fe": 1.0,
                "P": 1.0,
                "O": 4.0,
            }
        }

    This function deliberately does not parse formula strings or infer
    stoichiometry from element membership.
    """
    if not isinstance(raw_data, dict):
        return None

    composition = raw_data.get("composition")

    if not isinstance(composition, dict) or not composition:
        return None

    amounts: dict[str, float] = {}

    for raw_symbol, raw_amount in composition.items():
        symbol = str(raw_symbol).strip()

        if not symbol:
            raise ValueError(
                "Stored composition contains an empty element symbol"
            )

        try:
            amounts[symbol] = float(raw_amount)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Stored composition contains a non-numeric amount "
                f"for element {symbol}: {raw_amount!r}"
            ) from exc

    return amounts


def load_material_element_rows(
    db: Session,
    material_id: int,
) -> list[tuple[MaterialElement, Element]]:
    return (
        db.query(MaterialElement, Element)
        .join(
            Element,
            MaterialElement.element_id == Element.id,
        )
        .filter(MaterialElement.material_id == material_id)
        .all()
    )


def backfill_material(
    db: Session,
    material: Material,
) -> MaterialBackfillResult:
    composition_amounts = extract_composition_amounts(material.raw_data)

    if composition_amounts is None:
        raise ValueError(
            "Structured raw_data['composition'] is unavailable"
        )

    corrected_fractions = (
        MaterialCompositionService.normalize_amounts(
            composition_amounts
        )
    )

    rows = load_material_element_rows(
        db=db,
        material_id=material.id,
    )

    if not rows:
        raise ValueError(
            "Material has no MaterialElement rows"
        )

    rows_by_symbol = {
        element.symbol: material_element
        for material_element, element in rows
    }

    database_symbols = set(rows_by_symbol)
    composition_symbols = set(corrected_fractions)

    missing_database_symbols = sorted(
        composition_symbols - database_symbols
    )
    unexpected_database_symbols = sorted(
        database_symbols - composition_symbols
    )

    if missing_database_symbols or unexpected_database_symbols:
        raise ValueError(
            "Stored MaterialElement membership does not match structured "
            "composition: "
            f"missing_database_symbols={missing_database_symbols}, "
            f"unexpected_database_symbols={unexpected_database_symbols}"
        )

    corrected_total = sum(corrected_fractions.values())

    if not isclose(
        corrected_total,
        1.0,
        abs_tol=FRACTION_SUM_ABS_TOLERANCE,
    ):
        raise ValueError(
            "Normalized composition fractions do not sum to 1.0: "
            f"{corrected_total!r}"
        )

    previous_fractions = {
        symbol: float(rows_by_symbol[symbol].fraction)
        for symbol in sorted(rows_by_symbol)
    }

    changed_links = 0

    for symbol, corrected_fraction in corrected_fractions.items():
        link = rows_by_symbol[symbol]
        previous_fraction = float(link.fraction)

        if not isclose(
            previous_fraction,
            corrected_fraction,
            abs_tol=FRACTION_SUM_ABS_TOLERANCE,
        ):
            link.fraction = corrected_fraction
            changed_links += 1

    return MaterialBackfillResult(
        material_id=material.id,
        mp_id=material.mp_id,
        formula=material.pretty_formula or material.formula,
        changed_links=changed_links,
        previous_fractions=previous_fractions,
        corrected_fractions={
            symbol: corrected_fractions[symbol]
            for symbol in sorted(corrected_fractions)
        },
    )


def find_materials(
    db: Session,
    mp_id: str | None,
) -> list[Material]:
    query = (
        db.query(Material)
        .filter(Material.source == "materials_project")
        .order_by(Material.id)
    )

    if mp_id is not None:
        query = query.filter(Material.mp_id == mp_id)

    return query.all()


def print_material_result(
    result: MaterialBackfillResult,
) -> None:
    status = (
        "UPDATED"
        if result.changed_links > 0
        else "UNCHANGED"
    )

    print(
        f"{status}: "
        f"id={result.material_id}, "
        f"mp_id={result.mp_id}, "
        f"formula={result.formula}, "
        f"changed_links={result.changed_links}"
    )

    print(f"  before={result.previous_fractions}")
    print(f"  after ={result.corrected_fractions}")


def run_backfill(
    db: Session,
    *,
    apply_changes: bool,
    mp_id: str | None = None,
) -> BackfillSummary:
    summary = BackfillSummary()
    materials = find_materials(db=db, mp_id=mp_id)

    summary.discovered = len(materials)

    failures: list[str] = []

    for material in materials:
        if material.mp_id.startswith("mp-test-"):
            summary.skipped_test_materials += 1
            print(
                f"SKIPPED TEST: "
                f"id={material.id}, mp_id={material.mp_id}"
            )
            continue

        if extract_composition_amounts(material.raw_data) is None:
            summary.skipped_missing_composition += 1
            print(
                f"SKIPPED NO COMPOSITION: "
                f"id={material.id}, "
                f"mp_id={material.mp_id}, "
                f"formula={material.pretty_formula or material.formula}"
            )
            continue

        summary.eligible += 1

        try:
            result = backfill_material(
                db=db,
                material=material,
            )
        except ValueError as exc:
            summary.failed_materials += 1

            failure = (
                f"id={material.id}, "
                f"mp_id={material.mp_id}, "
                f"formula={material.pretty_formula or material.formula}: "
                f"{exc}"
            )
            failures.append(failure)

            print(f"FAILED: {failure}")
            continue

        print_material_result(result)

        if result.changed_links > 0:
            summary.updated_materials += 1
            summary.updated_links += result.changed_links
        else:
            summary.unchanged_materials += 1

    if failures:
        db.rollback()

        failure_lines = "\n".join(
            f"- {failure}"
            for failure in failures
        )

        raise RuntimeError(
            "Backfill validation failed. No changes were committed.\n"
            f"{failure_lines}"
        )

    if apply_changes:
        db.commit()
    else:
        db.rollback()

    return summary


def print_summary(
    summary: BackfillSummary,
    *,
    applied: bool,
) -> None:
    mode = "APPLY" if applied else "DRY RUN"

    print("\n" + "=" * 72)
    print(f"Material fraction backfill summary — {mode}")
    print("=" * 72)
    print(f"Discovered:                 {summary.discovered}")
    print(f"Eligible:                   {summary.eligible}")
    print(f"Updated materials:          {summary.updated_materials}")
    print(f"Updated links:              {summary.updated_links}")
    print(f"Already correct:            {summary.unchanged_materials}")
    print(f"Skipped test materials:     {summary.skipped_test_materials}")
    print(
        "Skipped missing composition: "
        f"{summary.skipped_missing_composition}"
    )
    print(f"Failed materials:           {summary.failed_materials}")

    if applied:
        print("\nChanges committed.")
    else:
        print("\nDry run completed. Changes rolled back.")


def main() -> None:
    args = parse_args()
    db = SessionLocal()

    try:
        summary = run_backfill(
            db=db,
            apply_changes=args.apply,
            mp_id=args.mp_id,
        )

        print_summary(
            summary,
            applied=args.apply,
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()