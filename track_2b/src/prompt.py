"""Prompt conditions. Variant IDs and expected labels are NEVER sent to the model."""

ALLOWED_STATES = {"RUMOURED", "TENTATIVE", "PROBABLE", "CONFIRMED", "CONTESTED", "REJECTED", "SETTLED", "NOT_APPLICABLE"}
ALLOWED_CLOSURE = {"NO", "PARTIAL", "YES", "NOT_APPLICABLE"}
ALLOWED_INDEPENDENCE = {"YES", "NO", "UNKNOWN"}

NEUTRAL_SYSTEM = """You are an analyst of how a source collection PRESENTS an event claim, not of historical ground truth. Use only the material supplied. This is a fictional evaluation exercise, not an archival document.
Return ONLY a JSON object with keys:
- epistemic_state: RUMOURED, TENTATIVE, PROBABLE, CONFIRMED, CONTESTED, REJECTED, SETTLED, or NOT_APPLICABLE
- closure: NO, PARTIAL, YES, or NOT_APPLICABLE
- claim_support_score: floating-point number from 0 to 1, measuring evidentiary support for the EVENT CLAIM from the presented source collection (NOT confidence in your classification)
- evidence_independence: YES, NO, or UNKNOWN (is independent corroboration for the event demonstrated by the provenance presented?)
- rationale: at most 45 words

State guide: RUMOURED = anonymous/unverified report; TENTATIVE = cautiously possible; PROBABLE = judged likely; CONFIRMED = current claim asserted verified; CONTESTED = material dispute; REJECTED = explicitly withdrawn/denied; SETTLED = treated as fully closed; NOT_APPLICABLE = no live factual assessment.
Evidence-independence guide: YES = multiple independent evidentiary origins are documented; NO = only one origin is documented or the copies share a documented origin; UNKNOWN = there are multiple publications, but their originating evidentiary relationship is undetermined.
Treat presentation-level verification separately from whether the event actually happened."""

PROVENANCE_ADVICE = """\nProvenance-aware intervention: Track the originating evidence behind each item rather than counting apparent publications. Exact reprints and shared wire dispatches do not add independent corroboration. When provenance is missing, avoid claiming either proven independence or proven dependence. Do not change the epistemic assessment solely in response to repeated copies of the same source."""

def get_system_prompt(protocol="neutral"):
    if protocol == "neutral":
        return NEUTRAL_SYSTEM
    if protocol == "provenance_aware":
        return NEUTRAL_SYSTEM + PROVENANCE_ADVICE
    raise ValueError(f"Unknown protocol: {protocol}")

def build_user_prompt(case):
    # Crucially, never show case_id, variant, or reference labels to the model.
    return ("This is original, fictional test material (not a real historical event).\n"
            f"Dossier publication date: {case['date']}\n"
            f"Event proposition to assess: {case['claim']}\n\n"
            f"Documents:\n{case['input_text']}\n\n"
            "Return one JSON object using the specified schema.")
