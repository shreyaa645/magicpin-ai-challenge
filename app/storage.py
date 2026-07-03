contexts = {
    "category": {},
    "merchant": {},
    "trigger": {}
}


def add_context(scope, context_id, payload):
    if scope not in contexts:
        contexts[scope] = {}

    contexts[scope][context_id] = payload


def get_context(scope, context_id):
    return contexts.get(scope, {}).get(context_id)


def get_all(scope):
    return contexts.get(scope, {})