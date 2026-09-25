from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Tashkent")


def next_lesson(schedules: list[dict], now: datetime | None = None) -> tuple[datetime, dict] | None:
    """Hozirdan keyingi eng yaqin dars: (boshlanish vaqti, slot). Jadval bo'sh bo'lsa None."""
    now = now or datetime.now(TZ)
    best = None
    for s in schedules:
        hour, minute = map(int, s["startTime"].split(":"))
        for offset in range(8):
            day = now.date() + timedelta(days=offset)
            if day.isoweekday() != s["weekday"]:
                continue
            start = datetime(day.year, day.month, day.day, hour, minute, tzinfo=TZ)
            if start <= now:
                continue  # bugungi dars o'tib ketgan, keyingi haftaga o'tamiz
            if best is None or start < best[0]:
                best = (start, s)
            break
    return best