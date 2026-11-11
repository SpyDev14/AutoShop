def typename(obj: object | type) -> str:
    if isinstance(obj, type):
        return obj.__name__
    return type(obj).__name__
