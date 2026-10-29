from typing import Tuple, List, Optional, Any
from pydantic import ValidationError
from app.schemas.verification import SynthesizerOutput


def validate_synthesizer_output(raw_output: Any) -> Tuple[bool, List[str], Optional[SynthesizerOutput]]:
    """
    Validates synthesizer structured output against Pydantic schema and guardrails rules:
    - Output must be non-empty.
    - Claims must have valid claim IDs.
    - Each claim must cite at least one evidence ID or explicitly note uncertainty.
    - Claims must not be vacuous or generic placeholders.
    """
    errors: List[str] = []

    if not raw_output:
        return False, ["Synthesizer returned empty response"], None

    if isinstance(raw_output, dict):
        try:
            output = SynthesizerOutput(**raw_output)
        except ValidationError as ve:
            return False, [f"Schema validation error: {err['loc']} - {err['msg']}" for err in ve.errors()], None
    elif isinstance(raw_output, SynthesizerOutput):
        output = raw_output
    else:
        return False, [f"Unexpected output type: {type(raw_output)}"], None

    if not output.draft_answer or not output.draft_answer.strip():
        errors.append("Draft answer cannot be empty.")

    if not output.claims:
        errors.append("Synthesizer failed to decompose answer into individual factual claims.")
    else:
        for idx, claim in enumerate(output.claims):
            if not claim.claim_id:
                errors.append(f"Claim at index {idx} has missing claim_id.")
            if not claim.claim_text or len(claim.claim_text.strip()) < 5:
                errors.append(f"Claim '{claim.claim_id}' has trivial or empty claim_text.")
            if not claim.evidence_ids and not output.uncertainty:
                errors.append(f"Claim '{claim.claim_id}' cites zero evidence IDs and no uncertainty is declared.")

    if errors:
        return False, errors, output

    return True, [], output
