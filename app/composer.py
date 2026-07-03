def generate_reply(message: str) -> str:
    """
    Temporary rule-based reply.
    Gemini will replace this later.
    """

    msg = message.lower()

    if any(x in msg for x in [
        "ok",
        "okay",
        "yes",
        "sure",
        "let's do it",
        "lets do it",
        "proceed",
        "start"
    ]):
        return "Perfect! I'll start the onboarding process and guide you through the next steps."

    if any(x in msg for x in [
        "stop",
        "spam",
        "leave me",
        "don't message",
        "dont message"
    ]):
        return "I'm sorry for the inconvenience. We won't bother you again."

    return "Thanks for your message. How can I help you today?"