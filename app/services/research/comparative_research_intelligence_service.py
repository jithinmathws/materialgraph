class ComparativeResearchIntelligenceService:
    EVIDENCE_READINESS_ORDER = {
        "strong": 3,
        "moderate": 2,
        "limited": 1,
    }

    def compare_opportunities(
        self,
        opportunities: list[dict],
    ) -> dict:
        if not opportunities:
            return self._empty_comparison()

        return {
            "comparison_count": len(opportunities),
            "top_ranked_pathway": self._top_ranked_pathway(
                opportunities
            ),
            "comparative_strengths": self._comparative_strengths(
                opportunities
            ),
            "comparative_trade_offs": self._comparative_trade_offs(
                opportunities
            ),
            "comparative_research_gaps": self._comparative_research_gaps(
                opportunities
            ),
            "comparative_evidence_readiness": (
                self._comparative_evidence_readiness(opportunities)
            ),
            "comparative_assumptions": self._comparative_assumptions(
                opportunities
            ),
            "researcher_decision_required": True,
            "decision_boundary": (
                "MaterialGraph compares existing pathway opportunities using "
                "deterministic, explainable outputs. Researchers remain "
                "responsible for scientific selection, validation, and "
                "experimental decisions."
            ),
            "pairwise_comparisons": self._pairwise_comparisons(opportunities),
            "comparative_element_highlights": self._comparative_element_highlights(opportunities),
        }

    def _top_ranked_pathway(
        self,
        opportunities: list[dict],
    ) -> dict:
        top = max(
            opportunities,
            key=lambda item: item.get(
                "scientific_usefulness_score",
                0.0,
            ),
        )

        return {
            "rank": top.get("rank"),
            "scientific_usefulness_score": top.get(
                "scientific_usefulness_score",
                0.0,
            ),
            "why_it_ranks_highest": self._top_pathway_reasons(top),
        }

    def _top_pathway_reasons(
        self,
        opportunity: dict,
    ) -> list[str]:
        breakdown = opportunity.get("score_breakdown", {})
        reasons = []

        ordered_components = sorted(
            breakdown.items(),
            key=lambda item: (-item[1], item[0]),
        )

        for component, score in ordered_components[:3]:
            if score > 0:
                reasons.append(
                    f"{self._humanize(component)} contributes {score:.2f} points."
                )

        return reasons or [
            "This pathway has the highest scientific usefulness score "
            "among the compared opportunities."
        ]

    def _comparative_strengths(
        self,
        opportunities: list[dict],
    ) -> list[dict]:
        return [
            {
                "rank": opportunity.get("rank"),
                "strengths": list(
                    opportunity.get("strengths", [])
                ),
            }
            for opportunity in opportunities
        ]

    def _comparative_trade_offs(
        self,
        opportunities: list[dict],
    ) -> list[dict]:
        return [
            {
                "rank": opportunity.get("rank"),
                "trade_offs": list(
                    opportunity.get("trade_offs", [])
                ),
                "risks": list(
                    opportunity.get("risks", [])
                ),
            }
            for opportunity in opportunities
        ]

    def _comparative_research_gaps(
        self,
        opportunities: list[dict],
    ) -> list[dict]:
        return [
            {
                "rank": opportunity.get("rank"),
                "missing_evidence": list(
                    opportunity.get(
                        "evidence_summary",
                        {},
                    ).get(
                        "missing_evidence",
                        [],
                    )
                ),
            }
            for opportunity in opportunities
        ]

    def _comparative_evidence_readiness(
        self,
        opportunities: list[dict],
    ) -> dict:
        readiness_by_pathway = [
            {
                "rank": opportunity.get("rank"),
                "evidence_readiness": opportunity.get(
                    "evidence_summary",
                    {},
                ).get(
                    "evidence_readiness",
                    "limited",
                ),
            }
            for opportunity in opportunities
        ]

        highest = max(
            readiness_by_pathway,
            key=lambda item: (
                self.EVIDENCE_READINESS_ORDER.get(
                    item["evidence_readiness"],
                    0,
                ),
                -self._rank_sort_value(item.get("rank")),
            ),
        )

        return {
            "pathways": readiness_by_pathway,
            "highest_readiness_pathway_rank": highest.get("rank"),
            "highest_readiness": highest.get(
                "evidence_readiness"
            ),
        }

    def _comparative_assumptions(
        self,
        opportunities: list[dict],
    ) -> list[dict]:
        return [
            {
                "rank": opportunity.get("rank"),
                "pathway_assumptions": list(
                    opportunity.get("assumptions", [])
                ),
                "weak_assumptions": list(
                    opportunity.get(
                        "evidence_summary",
                        {},
                    ).get(
                        "weak_assumptions",
                        [],
                    )
                ),
            }
            for opportunity in opportunities
        ]

    def _empty_comparison(self) -> dict:
        return {
            "comparison_count": 0,
            "top_ranked_pathway": None,
            "comparative_strengths": [],
            "comparative_trade_offs": [],
            "comparative_research_gaps": [],
            "comparative_evidence_readiness": {
                "pathways": [],
                "highest_readiness_pathway_rank": None,
                "highest_readiness": None,
            },
            "comparative_assumptions": [],
            "researcher_decision_required": True,
            "decision_boundary": (
                "No pathway opportunities were available for comparison. "
                "Researchers remain responsible for scientific selection, "
                "validation, and experimental decisions."
            ),
            "pairwise_comparisons": [],
            "comparative_element_highlights": [],
        }

    def _humanize(self, value: str) -> str:
        return value.replace("_", " ").capitalize()

    def _rank_sort_value(
        self,
        rank: int | None,
    ) -> int:
        return rank if rank is not None else 10**9

    def _pairwise_comparisons(
        self,
        opportunities: list[dict],
    ) -> list[dict]:
        ranked = sorted(
            opportunities,
            key=lambda item: item.get("scientific_usefulness_score", 0.0),
            reverse=True,
        )

        comparisons = []

        for higher, lower in zip(ranked, ranked[1:]):
            comparisons.append(
                self._compare_pair(
                    higher=higher,
                    lower=lower,
                )
            )

        return comparisons


    def _compare_pair(
        self,
        higher: dict,
        lower: dict,
    ) -> dict:
        higher_score = higher.get("scientific_usefulness_score", 0.0)
        lower_score = lower.get("scientific_usefulness_score", 0.0)
        score_difference = round(higher_score - lower_score, 2)

        return {
            "first_pathway_rank": higher.get("rank"),
            "second_pathway_rank": lower.get("rank"),

            # Backward-compatible aliases.
            # Can be removed in a future API cleanup if desired.
            "higher_ranked_pathway_rank": higher.get("rank"),
            "lower_ranked_pathway_rank": lower.get("rank"),
            "score_difference": score_difference,
            "comparison_type": (
                "tie"
                if score_difference == 0
                else "score_difference"
            ),
            "tie_reason": self._tie_reason(
                higher=higher,
                lower=lower,
                score_difference=score_difference,
            ),
            "endpoint_material_comparison": (
                self._endpoint_material_comparison(
                    higher=higher,
                    lower=lower,
                )
            ),
            "why_higher_ranked": self._higher_ranked_reasons(
                higher=higher,
                lower=lower,
            ),
            "lower_ranked_pathway_advantages": (
                self._lower_ranked_advantages(
                    higher=higher,
                    lower=lower,
                )
            ),
            "evidence_readiness_comparison": (
                self._evidence_readiness_pair_comparison(
                    higher=higher,
                    lower=lower,
                )
            ),
        }

    def _tie_reason(
        self,
        *,
        higher: dict,
        lower: dict,
        score_difference: float,
    ) -> str | None:
        if score_difference != 0:
            return None

        higher_endpoint = self._endpoint_material(higher)
        lower_endpoint = self._endpoint_material(lower)

        if higher_endpoint != lower_endpoint:
            return (
                "Both pathways have the same deterministic scientific usefulness score, "
                "but they end at different material opportunities. Researchers should "
                "compare endpoint material properties, synthesis feasibility, literature "
                "support, electrochemical behavior, and experimental validation needs."
            )

        return (
            "Both pathways have the same deterministic scientific usefulness score. "
            "Researchers should use external evidence and domain judgment to decide "
            "whether either pathway deserves priority."
        )


    def _endpoint_material_comparison(
        self,
        *,
        higher: dict,
        lower: dict,
    ) -> dict:
        first_endpoint = self._endpoint_material(higher)
        second_endpoint = self._endpoint_material(lower)

        return {
            "first_pathway_endpoint": first_endpoint,
            "second_pathway_endpoint": second_endpoint,

            # Backward-compatible aliases.
            "higher_ranked_endpoint": first_endpoint,
            "lower_ranked_endpoint": second_endpoint,

            "same_endpoint": first_endpoint == second_endpoint,
        }


    def _endpoint_material(
        self,
        opportunity: dict,
    ) -> dict | None:
        materials = opportunity.get("pathway", {}).get("materials", [])

        if not materials:
            return None

        endpoint = materials[-1]

        return {
            "material_id": endpoint.get("material_id"),
            "formula": endpoint.get("formula"),
            "pretty_formula": endpoint.get("pretty_formula"),
            "mp_id": endpoint.get("mp_id"),
        }

    def _higher_ranked_reasons(
        self,
        higher: dict,
        lower: dict,
    ) -> list[dict]:
        higher_breakdown = higher.get("score_breakdown", {})
        lower_breakdown = lower.get("score_breakdown", {})

        reasons = []

        for dimension, higher_score in higher_breakdown.items():
            lower_score = lower_breakdown.get(dimension, 0.0)
            difference = round(higher_score - lower_score, 2)

            if difference <= 0:
                continue

            reasons.append({
                "dimension": dimension,
                "higher_score": higher_score,
                "lower_score": lower_score,
                "difference": difference,
                "explanation": (
                    f"Higher-ranked pathway has stronger "
                    f"{self._humanize(dimension)} signal."
                ),
            })

        return reasons


    def _lower_ranked_advantages(
        self,
        higher: dict,
        lower: dict,
    ) -> list[dict]:
        higher_breakdown = higher.get("score_breakdown", {})
        lower_breakdown = lower.get("score_breakdown", {})

        advantages = []

        for dimension, lower_score in lower_breakdown.items():
            higher_score = higher_breakdown.get(dimension, 0.0)
            difference = round(lower_score - higher_score, 2)

            if difference <= 0:
                continue

            advantages.append({
                "dimension": dimension,
                "higher_ranked_score": higher_score,
                "lower_ranked_score": lower_score,
                "difference": difference,
                "explanation": (
                    f"Lower-ranked pathway has stronger "
                    f"{self._humanize(dimension)} signal despite ranking lower overall."
                ),
            })

        return advantages


    def _evidence_readiness_pair_comparison(
        self,
        higher: dict,
        lower: dict,
    ) -> dict:
        higher_readiness = higher.get("evidence_summary", {}).get(
            "evidence_readiness",
            "limited",
        )
        lower_readiness = lower.get("evidence_summary", {}).get(
            "evidence_readiness",
            "limited",
        )

        return {
            "higher_ranked_pathway_readiness": higher_readiness,
            "lower_ranked_pathway_readiness": lower_readiness,
            "same_readiness": higher_readiness == lower_readiness,
        }

    def _comparative_element_highlights(
        self,
        opportunities: list[dict],
    ) -> list[dict]:
        element_roles: dict[tuple[str, str], set[int]] = {}

        for opportunity in opportunities:
            rank = opportunity.get("rank")
            facts = opportunity.get("scientific_facts", {})

            self._collect_element_roles(
                element_roles=element_roles,
                elements=facts.get("introduced_elements", []),
                role="introduced_element",
                rank=rank,
            )
            self._collect_element_roles(
                element_roles=element_roles,
                elements=facts.get("removed_elements", []),
                role="removed_element",
                rank=rank,
            )
            self._collect_element_roles(
                element_roles=element_roles,
                elements=facts.get("preserved_framework", []),
                role="preserved_framework",
                rank=rank,
            )

        highlights = [
            self._build_element_highlight(
                element=element,
                role=role,
                ranks=sorted(ranks),
            )
            for (element, role), ranks in element_roles.items()
        ]

        highlights.sort(
            key=lambda item: (
                -len(item["appears_in_pathway_ranks"]),
                item["element"],
                item["role"],
            )
        )

        return highlights


    def _collect_element_roles(
        self,
        *,
        element_roles: dict[tuple[str, str], set[int]],
        elements: list[str],
        role: str,
        rank: int | None,
    ) -> None:
        if rank is None:
            return

        for element in elements:
            key = (element, role)
            element_roles.setdefault(key, set()).add(rank)


    def _build_element_highlight(
        self,
        *,
        element: str,
        role: str,
        ranks: list[int],
    ) -> dict:
        return {
            "element": element,
            "role": role,
            "appears_in_pathway_ranks": ranks,
            "potential_signal": self._element_potential_signal(
                element=element,
                role=role,
                ranks=ranks,
            ),
            "researcher_action": self._element_researcher_action(
                element=element,
                role=role,
            ),
            "requires_validation": True,
        }


    def _element_potential_signal(
        self,
        *,
        element: str,
        role: str,
        ranks: list[int],
    ) -> str:
        if role == "introduced_element":
            return (
                f"{element} appears as an introduced element in "
                f"{len(ranks)} compared pathway(s)."
            )

        if role == "removed_element":
            return (
                f"{element} appears as a removed or avoided element in "
                f"{len(ranks)} compared pathway(s)."
            )

        if role == "preserved_framework":
            return (
                f"{element} appears as part of preserved framework chemistry in "
                f"{len(ranks)} compared pathway(s)."
            )

        return (
            f"{element} appears in {len(ranks)} compared pathway(s)."
        )


    def _element_researcher_action(
        self,
        *,
        element: str,
        role: str,
    ) -> str:
        if role == "introduced_element":
            return (
                f"Verify whether introducing {element} preserves the target "
                "scientific or application behavior."
            )

        if role == "removed_element":
            return (
                f"Verify whether removing or avoiding {element} improves the "
                "research objective without harming required properties."
            )

        if role == "preserved_framework":
            return (
                f"Verify whether {element}-containing framework chemistry remains "
                "stable, functional, and experimentally plausible."
            )

        return (
            f"Review the scientific role of {element} before prioritizing this pathway."
        )