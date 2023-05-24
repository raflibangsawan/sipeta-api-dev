def to_bool(str: str) -> bool:
    return str is not None and bool(str.lower() in ("yes", "true", "t", "1"))
