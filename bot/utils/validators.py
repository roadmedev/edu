import re


def parse_time(text: str) -> str | None:
    """'14:00', '14.00', '9:30', '9' -> 'HH:MM'; noto'g'ri bo'lsa None"""
    m = re.fullmatch(r"(\d{1,2})(?:[:.](\d{2}))?", text.strip())
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2) or 0)
    if h > 23 or mi > 59:
        return None
    return f"{h:02d}:{mi:02d}"


def parse_price(text: str) -> int | None:
    """'400 000', '400.000', '400000' -> 400000"""
    digits = re.sub(r"[\s.,']", "", text)
    if not digits.isdigit():
        return None
    value = int(digits)
    return value if 10_000 <= value <= 100_000_000 else None\


def parse_price_allow_zero(text: str) -> int | None:
    digits = re.sub(r"[\s.,']", "", text)
    if not digits.isdigit():
        return None
    value = int(digits)
    return value if 0 <= value <= 100_000_000 else None