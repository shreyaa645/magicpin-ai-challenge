AUTO_REPLY_PATTERNS = [
    "thank you for contacting",
    "we will get back",
    "our team will respond",
    "automated assistant",
    "auto reply",
    "out of office"
]


def generate_reply(message: str):

    msg = message.lower()

    if any(x in msg for x in AUTO_REPLY_PATTERNS):
        return {
            "action": "end",
            "body": ""
        }

    if any(x in msg for x in [
        "join",
        "lets do it",
        "let's do it",
        "go ahead",
        "yes",
        "proceed"
    ]):
        return {
            "action": "send",
            "body": "Perfect! I'll start the onboarding process and guide you through the next steps."
        }

    if any(x in msg for x in [
        "spam",
        "stop",
        "leave me",
        "don't message",
        "dont message"
    ]):
        return {
            "action": "end",
            "body": ""
        }

    return {
        "action": "send",
        "body": "Thanks! I'll help you with that."
    }