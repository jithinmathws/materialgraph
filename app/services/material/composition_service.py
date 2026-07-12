from math import isfinite
from typing import Mapping


class MaterialCompositionService:
    """
    Canonical validation and normalization rules for material composition.

    Composition amounts represent stoichiometric quantities such as:

        {"Li": 1, "Fe": 1, "P": 1, "O": 4}

    Composition fractions represent normalized weights such as:

        {
            "Li": 1 / 7,
            "Fe": 1 / 7,
            "P": 1 / 7,
            "O": 4 / 7,
        }

    The service does not parse chemical formula strings. Structured
    composition data remains the canonical source for stoichiometry.
    """

    @classmethod
    def normalize_amounts(
        cls,
        composition: Mapping[str, float],
    ) -> dict[str, float]:
        """
        Validate stoichiometric amounts and normalize them to sum to 1.
        """
        validated_amounts = cls._validate_positive_values(
            values=composition,
            value_name="composition amount",
        )

        if not validated_amounts:
            raise ValueError(
                "Material composition must contain at least one element"
            )

        return cls._normalize_values(validated_amounts)

    @classmethod
    def normalize_fractions(
        cls,
        elements: list[str],
        fractions: Mapping[str, float],
    ) -> dict[str, float]:
        """
        Validate that fraction membership exactly matches the supplied
        element membership and normalize the values to sum to 1.
        """
        normalized_elements = cls._normalize_element_membership(elements)

        if not normalized_elements:
            raise ValueError(
                "Material element membership must contain at least one element"
            )

        validated_fractions = cls._validate_positive_values(
            values=fractions,
            value_name="composition fraction",
        )

        cls._validate_matching_membership(
            elements=normalized_elements,
            composition_symbols=list(validated_fractions),
        )

        return cls._normalize_values(validated_fractions)

    @classmethod
    def resolve_import_fractions(
        cls,
        elements: list[str],
        composition_fractions: Mapping[str, float] | None,
    ) -> dict[str, float]:
        """
        Resolve fractions for persistence by the material importer.

        New Materials Project candidates provide structured normalized
        fractions. Legacy/manual candidates may omit composition data.

        For legacy candidates only, preserve the historical 1.0-per-element
        representation instead of inventing stoichiometric knowledge.
        """
        normalized_elements = cls._normalize_element_membership(elements)

        if not normalized_elements:
            raise ValueError(
                "Material element membership must contain at least one element"
            )

        if not composition_fractions:
            return {
                symbol: 1.0
                for symbol in normalized_elements
            }

        return cls.normalize_fractions(
            elements=normalized_elements,
            fractions=composition_fractions,
        )

    @staticmethod
    def _normalize_element_membership(
        elements: list[str],
    ) -> list[str]:
        normalized_elements: list[str] = []
        observed_symbols: set[str] = set()

        for raw_symbol in elements:
            symbol = str(raw_symbol).strip()

            if not symbol:
                raise ValueError(
                    "Material element membership contains an empty symbol"
                )

            if symbol in observed_symbols:
                continue

            observed_symbols.add(symbol)
            normalized_elements.append(symbol)

        return normalized_elements

    @staticmethod
    def _validate_positive_values(
        values: Mapping[str, float],
        value_name: str,
    ) -> dict[str, float]:
        validated: dict[str, float] = {}

        for raw_symbol, raw_value in values.items():
            symbol = str(raw_symbol).strip()

            if not symbol:
                raise ValueError(
                    f"Material {value_name} contains an empty element symbol"
                )

            if symbol in validated:
                raise ValueError(
                    "Material composition contains duplicate normalized "
                    f"element symbol: {symbol}"
                )

            value = float(raw_value)

            if not isfinite(value) or value <= 0:
                raise ValueError(
                    f"Material contains an invalid {value_name} "
                    f"for element {symbol}: {raw_value!r}"
                )

            validated[symbol] = value

        return validated

    @staticmethod
    def _validate_matching_membership(
        elements: list[str],
        composition_symbols: list[str],
    ) -> None:
        element_set = set(elements)
        composition_set = set(composition_symbols)

        missing_elements = sorted(element_set - composition_set)
        unexpected_elements = sorted(composition_set - element_set)

        if missing_elements or unexpected_elements:
            raise ValueError(
                "Material candidate element membership does not match "
                "composition fractions: "
                f"missing={missing_elements}, "
                f"unexpected={unexpected_elements}"
            )

    @staticmethod
    def _normalize_values(
        values: dict[str, float],
    ) -> dict[str, float]:
        total = sum(values.values())

        if not isfinite(total) or total <= 0:
            raise ValueError(
                "Material composition must have a positive finite total"
            )

        return {
            symbol: value / total
            for symbol, value in values.items()
        }