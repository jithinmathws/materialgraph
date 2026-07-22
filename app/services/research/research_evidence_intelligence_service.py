class ResearchEvidenceIntelligenceService:
    def enrich_opportunity(self, opportunity: dict) -> dict:
        evidence_summary = self.build_evidence_summary(opportunity)

        return {
            **opportunity,
            "evidence_summary": evidence_summary,
        }

    def build_evidence_summary(self, opportunity: dict) -> dict:
        supporting_signals = self._supporting_signals(opportunity)
        missing_evidence = self._missing_evidence()
        weak_assumptions = self._weak_assumptions(opportunity)
        validation_priorities = self._validation_priorities(opportunity)

        return {
            "supporting_signals": supporting_signals,
            "missing_evidence": missing_evidence,
            "weak_assumptions": weak_assumptions,
            "validation_priorities": validation_priorities,
            "evidence_readiness": self._evidence_readiness(
                supporting_signals=supporting_signals,
                weak_assumptions=weak_assumptions,
            ),
        }

    def _supporting_signals(self, opportunity: dict) -> list[dict]:
        signals = []

        score_breakdown = opportunity.get("score_breakdown", {})
        scientific_facts = opportunity.get("scientific_facts", {})
        quality_summary = opportunity.get("quality_summary", {})

        if score_breakdown.get("shared_element_continuity", 0.0) >= 20:
            signals.append({
                "statement": "Shared-element continuity is identified across the pathway.",
                "source_service": "DiscoveryPathRankingService",
                "derived_from": "shared_element_continuity",
                "confidence": "moderate",
            })

        if score_breakdown.get("objective_alignment", 0.0) >= 20:
            signals.append({
                "statement": "Pathway aligns with the stated research objective.",
                "source_service": "DiscoveryPathRankingService",
                "derived_from": "objective_alignment",
                "confidence": "high",
            })

        if score_breakdown.get("transition_plausibility", 0.0) >= 15:
            signals.append({
                "statement": "Transition plausibility is strong under deterministic rules.",
                "source_service": "DiscoveryPathRankingService",
                "derived_from": "transition_plausibility",
                "confidence": "high",
            })

        if quality_summary.get("average_quality_score", 0.0) >= 12:
            signals.append({
                "statement": "Average material quality is strong.",
                "source_service": "MaterialQualityService",
                "derived_from": "quality_score",
                "confidence": "high",
            })

        shared_elements = scientific_facts.get("shared_elements") or scientific_facts.get("preserved_framework", [])
        if shared_elements:
            signals.append({
                "statement": (f"Shared elements identified across transitions: {'-'.join(shared_elements)}. "
                              "Structural preservation is not validated."),
                "source_service": "DiscoveryChainService",
                "derived_from": "element_overlap",
                "confidence": "moderate",
            })

        removed = scientific_facts.get("removed_elements", [])
        if removed:
            signals.append({
                "statement": f"Pathway removes element(s): {', '.join(removed)}.",
                "source_service": "DiscoveryChainService",
                "derived_from": "removed_elements",
                "confidence": "high",
            })

        introduced = scientific_facts.get("introduced_elements", [])
        if introduced:
            signals.append({
                "statement": f"Pathway introduces element(s): {', '.join(introduced)}.",
                "source_service": "DiscoveryChainService",
                "derived_from": "introduced_elements",
                "confidence": "high",
            })

        return signals

    def _missing_evidence(self) -> list[dict]:
        return [
            {
                "statement": "Experimental synthesis evidence is unavailable.",
                "reason": "MaterialGraph does not ingest experimental synthesis datasets.",
                "researcher_action": "Consult experimental literature and synthesis reports.",
            },
            {
                "statement": "Electrochemical performance evidence is unavailable.",
                "reason": "Battery performance datasets are not yet integrated.",
                "researcher_action": "Compare against published capacity, voltage, cycling, and rate-performance data.",
            },
            {
                "statement": "Scientific literature support is not yet integrated.",
                "reason": "MaterialGraph currently uses deterministic graph and material-property signals only.",
                "researcher_action": "Search relevant publications before prioritizing experimental work.",
            },
            {
                "statement": "DFT validation is not performed by MaterialGraph.",
                "reason": "MaterialGraph does not run first-principles calculations.",
                "researcher_action": "Run DFT or use trusted computational databases for validation.",
            },
            {
                "statement": "Manufacturing feasibility is not evaluated.",
                "reason": "Processing, scale-up, and cost constraints are outside the current dataset.",
                "researcher_action": "Review synthesis route, precursor availability, processing conditions, and scalability.",
            },
        ]

    def _weak_assumptions(self, opportunity: dict) -> list[dict]:
        weak = []

        score_breakdown = opportunity.get("score_breakdown", {})
        scientific_facts = opportunity.get("scientific_facts", {})
        quality_summary = opportunity.get("quality_summary", {})

        if scientific_facts.get("shared_elements") or scientific_facts.get("preserved_framework"):
            weak.append({
                "assumption": ("Shared-element continuity may indicate compositional relatedness, "
                               "but does not establish structural preservation."),
                "based_on": "element-overlap transition metadata",
                "requires_validation": True,
            })

        if score_breakdown.get("path_efficiency", 0.0) < 10:
            weak.append({
                "assumption": "Multi-hop pathway steps remain scientifically meaningful.",
                "based_on": "path_efficiency score",
                "requires_validation": True,
            })

        if score_breakdown.get("transition_plausibility", 0.0) < 15:
            weak.append({
                "assumption": "Transition plausibility is sufficient for research exploration.",
                "based_on": "transition_plausibility score",
                "requires_validation": True,
            })

        if quality_summary.get("overall_quality") in {"weak", "unknown"}:
            weak.append({
                "assumption": "Material quality is sufficient for pathway consideration.",
                "based_on": "quality_summary.overall_quality",
                "requires_validation": True,
            })

        if not weak:
            weak.append({
                "assumption": "Current support is deterministic and graph-derived, not experimentally validated.",
                "based_on": "MaterialGraph scoring and relationship model",
                "requires_validation": True,
            })

        return weak

    def _validation_priorities(self, opportunity: dict) -> list[dict]:
        priorities = []
        priority = 1

        scientific_facts = opportunity.get("scientific_facts", {})
        score_breakdown = opportunity.get("score_breakdown", {})

        if score_breakdown.get("shared_element_continuity", 0.0) >= 20:
            priorities.append({
                "priority": priority,
                "action": "Validate whether shared-element continuity corresponds to structural preservation.",
                "reason": "Element overlap is a major contributor to the current scientific usefulness score.",
            })
            priority += 1

        if scientific_facts.get("introduced_elements"):
            priorities.append({
                "priority": priority,
                "action": "Validate whether introduced element(s) preserve target functionality.",
                "reason": "The pathway depends on substitution or introduction of new elements.",
            })
            priority += 1

        if scientific_facts.get("material_quality"):
            priorities.append({
                "priority": priority,
                "action": "Validate material stability and energy-above-hull assumptions.",
                "reason": "Material quality contributes to pathway ranking.",
            })
            priority += 1

        priorities.append({
            "priority": priority,
            "action": "Check literature for synthesis reports or related compounds.",
            "reason": "MaterialGraph does not yet include literature evidence.",
        })
        priority += 1

        priorities.append({
            "priority": priority,
            "action": "Run computational validation before experimental prioritization.",
            "reason": "MaterialGraph does not replace DFT or domain-specific simulation workflows.",
        })

        return priorities

    def _evidence_readiness(
        self,
        supporting_signals: list[dict],
        weak_assumptions: list[dict],
    ) -> str:
        signal_count = len(supporting_signals)
        weak_count = len(weak_assumptions)

        if signal_count >= 5 and weak_count <= 2:
            return "strong"

        if signal_count >= 3:
            return "moderate"

        return "limited"