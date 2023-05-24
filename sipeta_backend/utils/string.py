def to_bool(str: str) -> bool:
    return bool(str.lower() in ("yes", "true", "t", "1"))
