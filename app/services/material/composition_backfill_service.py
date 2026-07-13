from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Any

from sqlalchemy.orm import Session

from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.material.composition_service import (
    MaterialCompositionService,
)


FRACTION_SUM_ABS_TOLERANCE = 1e-9


@dataclass
class CompositionBackfillSummary:
    discovered: int = 0
    eligible: int = 0
    updated_materials: int = 0
    updated_links: int = 0
    unchanged_materials: int = 0
    skipped_test_materials: int = 0
    skipped_missing_composition: int = 0
    failed_materials: int = 0


@dataclass(frozen=True)
class MaterialCompositionBackfillResult:
    material_id: int
    mp_id: str
    formula: str
    changed_links: int
    previous_fractions: dict[str, float]
    corrected_fractions: dict[str, float]


class MaterialCompositionBackfillService:
    """
    Correct persisted MaterialElement fractions using structured
    Materials Project composition stored in Material.raw_data.

    The service never parses formula strings and never guesses missing
    stoichiometry. Structured composition remains the canonical source.
    """

    def __init__(self, db: Session):
        self.db = db

    def find_materials(
        self,
        mp_id: str | None = None,
    ) -> list[Material]:
        query = (
            self.db.query(Material)
            .filter(Material.source == "materials_project")
            .order_by(Material.id)
        )

        if mp_id is not None:
            query = query.filter(Material.mp_id == mp_id)

        return query.all()

    def run(
        self,
        *,
        apply_changes: bool,
        mp_id: str | None = None,
    ) -> CompositionBackfillSummary:
        summary = CompositionBackfillSummary()
        materials = self.find_materials(mp_id=mp_id)

        summary.discovered = len(materials)

        failures: list[str] = []

        for material in materials:
            if self._is_test_material(material):
                summary.skipped_test_materials += 1
                self._print_skipped_test_material(material)
                continue

            try:
                composition_amounts = self.extract_composition_amounts(
                    material.raw_data
                )
            except ValueError as exc:
                summary.failed_materials += 1

                failure = self._format_failure(
                    material=material,
                    error=exc,
                )
                failures.append(failure)

                print(f"FAILED: {failure}")
                continue

            if composition_amounts is None:
                summary.skipped_missing_composition += 1
                self._print_skipped_missing_composition(material)
                continue

            summary.eligible += 1

            try:
                result = self.backfill_material(
                    material=material,
                    composition_amounts=composition_amounts,
                )
            except ValueError as exc:
                summary.failed_materials += 1

                failure = self._format_failure(
                    material=material,
                    error=exc,
                )
                failures.append(failure)

                print(f"FAILED: {failure}")
                continue

            self.print_material_result(result)

            if result.changed_links > 0:
                summary.updated_materials += 1
                summary.updated_links += result.changed_links
            else:
                summary.unchanged_materials += 1

        if failures:
            self.db.rollback()

            failure_lines = "\n".join(
                f"- {failure}"
                for failure in failures
            )

            raise RuntimeError(
                "Composition fraction backfill validation failed. "
                "No changes were committed.\n"
                f"{failure_lines}"
            )

        if apply_changes:
            self.db.commit()
        else:
            self.db.rollback()

        return summary

    def backfill_material(
        self,
        material: Material,
        composition_amounts: dict[str, float] | None = None,
    ) -> MaterialCompositionBackfillResult:
        """
        Validate and correct all MaterialElement fractions for one material.

        The caller may supply already-extracted composition amounts to avoid
        extracting the same raw-data structure twice.
        """
        if composition_amounts is None:
            composition_amounts = self.extract_composition_amounts(
                material.raw_data
            )

        if composition_amounts is None:
            raise ValueError(
                "Structured raw_data['composition'] is unavailable"
            )

        corrected_fractions = (
            MaterialCompositionService.normalize_amounts(
                composition_amounts
            )
        )

        rows = self._load_material_element_rows(
            material_id=material.id
        )

        if not rows:
            raise ValueError(
                "Material has no MaterialElement rows"
            )

        rows_by_symbol = {
            element.symbol: material_element
            for material_element, element in rows
        }

        self._validate_membership(
            rows_by_symbol=rows_by_symbol,
            corrected_fractions=corrected_fractions,
        )

        corrected_total = sum(corrected_fractions.values())

        if not isclose(
            corrected_total,
            1.0,
            rel_tol=0.0,
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
                rel_tol=0.0,
                abs_tol=FRACTION_SUM_ABS_TOLERANCE,
            ):
                link.fraction = corrected_fraction
                changed_links += 1

        return MaterialCompositionBackfillResult(
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

    @staticmethod
    def extract_composition_amounts(
        raw_data: dict[str, Any] | None,
    ) -> dict[str, float] | None:
        """
        Extract a structured element-to-amount mapping from stored MP data.

        Examples accepted:

            {
                "composition": {
                    "Li": 4.0,
                    "Fe": 4.0,
                    "P": 4.0,
                    "O": 16.0,
                }
            }

        Formula parsing is deliberately not used.
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

    def _load_material_element_rows(
        self,
        material_id: int,
    ) -> list[tuple[MaterialElement, Element]]:
        return (
            self.db.query(MaterialElement, Element)
            .join(
                Element,
                MaterialElement.element_id == Element.id,
            )
            .filter(MaterialElement.material_id == material_id)
            .all()
        )

    @staticmethod
    def _validate_membership(
        rows_by_symbol: dict[str, MaterialElement],
        corrected_fractions: dict[str, float],
    ) -> None:
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
                "Stored MaterialElement membership does not match "
                "structured composition: "
                f"missing_database_symbols={missing_database_symbols}, "
                f"unexpected_database_symbols="
                f"{unexpected_database_symbols}"
            )

    @staticmethod
    def _is_test_material(material: Material) -> bool:
        return material.mp_id.startswith("mp-test-")

    @staticmethod
    def _format_failure(
        material: Material,
        error: Exception,
    ) -> str:
        formula = material.pretty_formula or material.formula

        return (
            f"id={material.id}, "
            f"mp_id={material.mp_id}, "
            f"formula={formula}: "
            f"{error}"
        )

    @staticmethod
    def _print_skipped_test_material(
        material: Material,
    ) -> None:
        print(
            "SKIPPED TEST: "
            f"id={material.id}, "
            f"mp_id={material.mp_id}"
        )

    @staticmethod
    def _print_skipped_missing_composition(
        material: Material,
    ) -> None:
        formula = material.pretty_formula or material.formula

        print(
            "SKIPPED NO COMPOSITION: "
            f"id={material.id}, "
            f"mp_id={material.mp_id}, "
            f"formula={formula}"
        )

    @staticmethod
    def print_material_result(
        result: MaterialCompositionBackfillResult,
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

    @staticmethod
    def print_summary(
        summary: CompositionBackfillSummary,
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
        print(
            "Skipped test materials:     "
            f"{summary.skipped_test_materials}"
        )
        print(
            "Skipped missing composition: "
            f"{summary.skipped_missing_composition}"
        )
        print(f"Failed materials:           {summary.failed_materials}")

        if applied:
            print("\nChanges committed.")
        else:
            print("\nDry run completed. Changes rolled back.")