from html import escape
from datetime import datetime
from utils.schedule import TZ

MONTHS = ["yanvar", "fevral", "mart", "aprel", "may", "iyun",
          "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"]

WEEKDAYS = {1: "dushanba", 2: "seshanba", 3: "chorshanba", 4: "payshanba",
            5: "juma", 6: "shanba", 7: "yakshanba"}


def money(n: int) -> str:
    return f"{n:,}".replace(",", " ") + " so'm"


def format_schedule(schedules: list[dict]) -> str:
    """Bir xil vaqtdagi kunlarni guruhlaydi: 'soat 14:00-17:00gacha (seshanba, payshanba)'"""
    groups: dict[tuple, list[str]] = {}
    for s in schedules:
        groups.setdefault((s["startTime"], s["endTime"]), []).append(WEEKDAYS[s["weekday"]])
    parts = [
        f"soat {start}-{end}gacha <i>({', '.join(days)})</i>"
        for (start, end), days in groups.items()
    ]
    return "; ".join(parts) or "belgilanmagan"


def format_course(c: dict) -> str:
    subject = f"📖 Fan: <b>{escape(c['subject'])}</b>\n" if c.get("subject") else ""
    return (
        f"O'qituvchi: <b>{escape(c['teacherName'])}</b>\n"
        f"📚 Kurs nomi: <b>{escape(c['title'])}</b>\n"
        f"{subject}"
        f"⏳ Davomiyligi: <b>{c['durationMonths']} oy</b>\n"
        f"🔄 Dars vaqti: <b>{format_schedule(c['schedules'])}</b>\n"
        f"💳 Narxi: <b>{money(c['price'])}</b> <i>(oyiga)</i>\n\n"
        f"{escape(c['description'])}"
    )


def format_timetable(courses: list[dict]) -> str:
    """Butun markazning haftalik jadvali (kunlar bo'yicha)"""
    by_day: dict[int, list[tuple]] = {}
    for c in courses:
        for s in c["schedules"]:
            by_day.setdefault(s["weekday"], []).append((s["startTime"], s["endTime"], c["title"]))

    if not by_day:
        return "Dars jadvali hozircha bo'sh."

    lines = ["🗓 <b>Haftalik dars jadvali</b>"]
    for day in sorted(by_day):
        lines.append(f"\n<b>{WEEKDAYS[day].capitalize()}</b>")
        for start, end, title in sorted(by_day[day]):
            lines.append(f"  {start}–{end} — {escape(title)}")
    return "\n".join(lines)


def format_date(d) -> str:
    return f"{d.day}-{MONTHS[d.month - 1]}"

def format_my_courses(items: list[dict]) -> str:
    if not items:
        return "Sizda hozircha faol kurs yo'q."
    lines = ["📚 <b>Mening kurslarim</b>"]
    for it in items:
        joined = it.get("joinedAt")
        since = format_date(datetime.fromisoformat(joined.replace("Z", "+00:00")).astimezone(TZ)) if joined else "—"
        att = (f"✅ {it['presentCount']} ta darsda qatnashgan, ❌ {it['absentCount']} ta darsni qoldirgan"
               if it["presentCount"] or it["absentCount"] else "Davomat hali belgilanmagan")
        lines.append(f"\n<b>{escape(it['courseTitle'])}</b>\n📅 Qatnashib kelayotgan sanasi: {since}\n{att}")
    return "\n".join(lines)


def format_rating(rows: list[dict]) -> str:
    if not rows:
        return "Hozircha reyting uchun yetarli statistika yo'q (davomat hali belgilanmagan)."
    lines = ["🏆 <b>Reyting</b> (darsga qatnashish bo'yicha)"]
    medals = ["🥇", "🥈", "🥉"]
    for i, r in enumerate(rows):
        prefix = medals[i] if i < 3 else f"{i + 1}."
        lines.append(f"{prefix} {escape(r['studentName'])} — {r['presentCount']} ta dars")
    return "\n".join(lines)


def format_student_list_header(data: dict) -> str:
    return (
        f"📚 <b>{escape(data['courseTitle'])}</b>\n"
        f"Narxi: {money(data['price'])} <i>(oyiga)</i>\n"
        f"O'quvchilar soni: {len(data['students'])}\n\nIsmni tanlang:"
    )


def format_student_detail(course_title: str, s: dict) -> str:
    debt = s["amountDue"] - s["amountPaid"]
    status_line = {
        "paid": "✅ To'liq to'langan",
        "partial": f"🟡 Qisman to'langan. Qarzi: {money(debt)}",
        "unpaid": f"🔴 To'lanmagan. Qarzi: {money(debt)}",
    }[s["status"]]
    return (
        f"👤 <b>{escape(s['studentName'])}</b>\n📞 {escape(s['studentPhone'])}\n📚 {escape(course_title)}\n\n"
        f"💳 To'lov: {money(s['amountPaid'])} / {money(s['amountDue'])}\n{status_line}"
    )


def format_payment_request(s: dict) -> str:
    return f"👤 <b>{escape(s['studentName'])}</b>\n💳 {money(s['amountDue'])} <i>(oyiga)</i>"


def format_balance(b: dict) -> str:
    return (
        f"💳 <b>Balans</b> ({b['period']})\n\n"
        f"👥 O'quvchilar: {b['studentsCount']} ta ({b['paidCount']} tasi to'lagan)\n"
        f"💰 Kutilayotgan summa: {money(b['totalDue'])}\n"
        f"✅ Tushgan summa: {money(b['totalPaid'])}\n"
        f"🔴 Qarzdorlik: {money(b['totalDebt'])}\n"
        f"📅 Bugungi kirim: {money(b['dailyIncome'])}"
    )


def format_stats(s: dict) -> str:
    return (
        f"📊 <b>Markaz statistikasi</b> ({s['period']})\n\n"
        f"🙍 Oddiy foydalanuvchilar: <b>{s['usersCount']}</b>\n"
        f"👨‍🏫 O'qituvchilar: <b>{s['teachersCount']}</b>\n"
        f"🎓 O'quvchilar: <b>{s['studentsCount']}</b>\n"
        f"📚 Faol kurslar: <b>{s['coursesCount']}</b>\n\n"
        f"💰 Kutilayotgan summa: {money(s['totalDue'])}\n"
        f"✅ Tushgan summa: {money(s['totalPaid'])}\n"
        f"🔴 Umumiy qarzdorlik: {money(s['totalDebt'])}"
    )


def format_plain_users(rows: list[dict]) -> str:
    if not rows:
        return "🙍 Oddiy foydalanuvchilar yo'q."
    lines = ["🙍 <b>Oddiy foydalanuvchilar</b>"]
    for r in rows:
        lines.append(f"\n👤 {escape(r['fullName'])}\n📞 {escape(r['phone'])} | 🆔 <code>{r['telegramId']}</code>")
    return "\n".join(lines)


def format_teacher_card(t: dict) -> str:
    subject = f"📖 Fan: <b>{escape(t['subject'])}</b>\n" if t.get("subject") else ""
    return f"👨‍🏫 <b>{escape(t['fullName'])}</b>\n📞 {escape(t['phone'])}\n{subject}"


def format_students_overview(students: list[dict]) -> str:
    if not students:
        return "🎓 Hozircha faol o'quvchi yo'q."
    lines = ["🎓 <b>O'quvchilar</b>\n"]
    for s in students:
        emoji = {"paid": "✅", "partial": "🟡"}.get(s["status"], "🔴")
        lines.append(f"{emoji} {escape(s['studentName'])} — {escape(s['courseTitle'])} ({escape(s['teacherName'])})")
    lines.append("\nTafsilot uchun ismni tanlang:")
    return "\n".join(lines)


def format_student_admin_detail(s: dict) -> str:
    debt = s["amountDue"] - s["amountPaid"]
    status_line = {
        "paid": "✅ To'liq to'langan",
        "partial": f"🟡 Qisman to'langan. Qarzi: {money(debt)}",
    }.get(s["status"], f"🔴 To'lanmagan. Qarzi: {money(debt)}")
    return (
        f"👤 <b>{escape(s['studentName'])}</b>\n"
        f"📚 Kurs: {escape(s['courseTitle'])}\n"
        f"👨‍🏫 O'qituvchi: {escape(s['teacherName'])}\n\n"
        f"💳 {money(s['amountPaid'])} / {money(s['amountDue'])}\n{status_line}"
    )

#Admin uchun
def format_finance(f: dict) -> str:
    return (
        "💰 <b>Moliya</b>\n\n"
        "Markaz ulushi (o'qituvchilar yig'gan pulning 30%):\n"
        f"⏳ Kutilayotgan: {money(f['totalDue'])}\n"
        f"✅ Yig'ilgan: {money(f['totalPaid'])}\n"
        f"🔴 Qarzdorlik: {money(f['totalDebt'])}"
    )


def format_payout_request(t: dict) -> str:
    return f"👨‍🏫 <b>{escape(t['teacherName'])}</b>\n💰 Ulush: {money(t['amountDue'])}"


def format_suggestions(rows: list[dict]) -> str:
    if not rows:
        return "📥 Taklif qutisi bo'sh."
    lines = ["📥 <b>Takliflar</b>"]
    for r in rows:
        lines.append(f"\n👤 {escape(r['fromName'])} ({r['fromRole']})\n💬 {escape(r['text'])}")
    return "\n".join(lines)