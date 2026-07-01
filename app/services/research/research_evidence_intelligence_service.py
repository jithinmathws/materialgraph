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
            "evidence_confidence": self._evidence_confidence(
                supporting_signals=supporting_signals,
                weak_assumptions=weak_assumptions,
            ),
        }

    def _supporting_signals(self, opportunity: dict) -> list[str]:
        signals = []

        score_breakdown = opportunity.get("score_breakdown", {})
        scientific_facts = opportunity.get("scientific_facts", {})
        quality_summary = opportunity.get("quality_summary", {})

        if score_breakdown.get("framework_preservation", 0.0) >= 20:
            signals.append("Strong framework-preservation signal.")

        if score_breakdown.get("objective_alignment", 0.0) >= 20:
            signals.append("Pathway aligns with the stated research objective.")

        if score_breakdown.get("transition_plausibility", 0.0) >= 15:
            signals.append("Transition plausibility is strong under current deterministic rules.")

        if quality_summary.get("average_quality_score", 0.0) >= 12:
            signals.append("Average material quality is strong.")

        if scientific_facts.get("preserved_framework"):
            framework = "-".join(scientific_facts["preserved_framework"])
            signals.append(f"Preserved framework chemistry identified: {framework}.")

        if scientific_facts.get("removed_elements"):
            removed = ", ".join(scientific_facts["removed_elements"])
            signals.append(f"Pathway removes element(s): {removed}.")

        if scientific_facts.get("introduced_elements"):
            introduced = ", ".join(scientific_facts["introduced_elements"])
            signals.append(f"Pathway introduces element(s): {introduced}.")

        return signals or ["No strong deterministic supporting evidence was identified."]

    def _missing_evidence(self) -> list[str]:
        return [
            "Experimental synthesis evidence is not available in MaterialGraph.",
            "Electrochemical performance data is not available in MaterialGraph.",
            "Scientific literature support is not yet integrated.",
            "DFT validation is not performed by MaterialGraph.",
            "Manufacturing feasibility is not evaluated.",
        ]

    def _weak_assumptions(self, opportunity: dict) -> list[str]:
        weak = []

        score_breakdown = opportunity.get("score_breakdown", {})
        quality_summary = opportunity.get("quality_summary", {})

        if score_breakdown.get("path_efficiency", 0.0) < 10:
            weak.append(
                "Multi-hop reasoning assumes intermediate pathway steps remain scientifically meaningful."
            )

        if score_breakdown.get("transition_plausibility", 0.0) < 15:
            weak.append(
                "Transition plausibility is moderate or weak under current scoring rules."
            )

        if quality_summary.get("overall_quality") in {"weak", "unknown"}:
            weak.append(
                "Material quality is weak or unknown for at least part of the pathway."
            )

        if not weak:
            weak.append(
                "Current assumptions are mostly structural and scoring-based, not experimentally validated."
            )

        return weak

    def _validation_priorities(self, opportunity: dict) -> list[str]:
        priorities = []

        scientific_facts = opportunity.get("scientific_facts", {})

        if scientific_facts.get("material_quality"):
            priorities.append("Validate material stability and energy-above-hull assumptions.")

        if scientific_facts.get("introduced_elements"):
            priorities.append("Validate whether introduced element(s) preserve target functionality.")

        if scientific_facts.get("preserved_framework"):
            priorities.append("Verify whether preserved framework chemistry supports comparable behavior.")

        priorities.extend(
            [
                "Check literature for synthesis reports or related compounds.",
                "Run computational validation before experimental prioritization.",
            ]
        )

        return priorities

    def _evidence_confidence(
        self,
        supporting_signals: list[str],
        weak_assumptions: list[str],
    ) -> str:
        signal_count = len([
            signal
            for signal in supporting_signals
            if not signal.startswith("No strong")
        ])

        weak_count = len(weak_assumptions)

        if signal_count >= 5 and weak_count <= 1:
            return "strong"

        if signal_count >= 3:
            return "moderate"

        return "limited"