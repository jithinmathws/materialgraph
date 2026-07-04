class DiscoveryWarningService:
    def build_warnings(
        self,
        candidates: list[dict],
        avoid_element: str | None,
        prefer_element: str | None,
        limit: int,
        total_candidate_count: int,
    ) -> list[str]:
        warnings = []

        if not candidates:
            warnings.append(
                "No discovery candidates were found for the requested constraints."
            )
            return warnings

        if prefer_element and not self._any_candidate_contains_element(
            candidates=candidates,
            element=prefer_element,
        ):
            warnings.append(
                f"No returned candidate contains the preferred element {prefer_element}."
            )

        if avoid_element and self._all_candidates_contain_element(
            candidates=candidates,
            element=avoid_element,
        ):
            warnings.append(
                f"All returned candidates still contain the avoided element {avoid_element}."
            )

        if total_candidate_count > limit:
            warnings.append(
                f"Results were limited to {limit} candidates from "
                f"{total_candidate_count} generated candidates."
            )

        return warnings

    def _any_candidate_contains_element(
        self,
        candidates: list[dict],
        element: str,
    ) -> bool:
        return any(
            element in candidate["formula"]
            for candidate in candidates
        )

    def _all_candidates_contain_element(
        self,
        candidates: list[dict],
        element: str,
    ) -> bool:
        return all(
            element in candidate["formula"]
            for candidate in candidates
        )