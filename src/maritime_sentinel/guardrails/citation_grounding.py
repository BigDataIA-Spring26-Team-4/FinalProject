"""Citation grounding — verify agent claims are backed by retrieved sources."""


def verify_citations(agent_output: dict, retrieved_context: list[dict]) -> tuple[bool, list[str]]:
    """Check that every citation source_id exists in the retrieved context.

    Returns (all_grounded, list_of_ungrounded_claim_ids).
    """
    # TODO: Extract citations from agent output, cross-check against context source_ids
    raise NotImplementedError
