"""Input moderation — filter off-topic and adversarial queries."""


def moderate_input(user_message: str) -> tuple[bool, str]:
    """Return (is_allowed, reason). Rejects off-topic/adversarial inputs."""
    # TODO: Keyword blocklist + LLM classifier for maritime relevance
    raise NotImplementedError
