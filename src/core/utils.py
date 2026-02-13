from datetime import UTC, datetime


def camel_to_snake(name: str) -> str:
    """Convert camel case to snake case."""
    if not name:
        return name
    name = name.replace("ORM", "")
    result = [name[0].lower()]
    for char in name[1:]:
        if char.isupper():
            prev_char = result[-1]
            if prev_char != "_" and not prev_char.isdigit():
                result.append("_")
            result.append(char.lower())
        else:
            result.append(char)
    return f"{''.join(result)}s"


def utcnow() -> datetime:
    """Returns the current UTC datetime."""
    return datetime.now(UTC)


__all__ = ("camel_to_snake", "utcnow")
