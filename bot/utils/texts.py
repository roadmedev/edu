from html import escape

from config import settings
from utils.formatters import WEEKDAYS, format_date
from utils.schedule import next_lesson

TERMS = (
    "📄 <b>Shartlar:</b>\n"
    "• Darslarga o'z vaqtida kelish talab qilinadi.\n"
    "• Kurs to'lovi har oy boshida o'qituvchiga to'lanadi.\n"
    "• Sababsiz 3 marta darsga kelmaslik o'rinni yo'qotishga\n"
     " va to'lovlarning kuyib ketishiga olib kelishi mumkin.\n"
    "• Markaz qoidalariga rioya qilish majburiy."
)

REJECTED = "😔 Kurs to'lgan yoki o'qituvchi sizni o'quvchilar safiga qo'shishni rad qildi."

HELP_TEXT = (
    "❓ <b>Yordam</b>\n\n"
    "• /start — Botni qayta ishga tushirish\n"
    "• «Kurslar» bo'limida yangi kursга yozilishingiz mumkin\n"
    "• Savol yoki muammo bo'lsa, pastdagi tugma orqali administratorga murojaat qiling"
)

def teacher_request(d: dict) -> str:
    return (
        "📩 <b>Kursga qo'shilish so'rovi</b>\n\n"
        f"👤 O'quvchi: <b>{escape(d['studentName'])}</b>\n"
        f"📞 Telefon: <b>{escape(d['studentPhone'])}</b>\n"
        f"📚 Kurs: <b>{escape(d['courseTitle'])}</b>"
    )


def student_accepted(d: dict) -> str:
    lesson = next_lesson(d["schedules"])
    if lesson:
        start, slot = lesson
        when = (f"<b>{WEEKDAYS[slot['weekday']]}</b> ({format_date(start)}) kuni "
                f"soat <b>{slot['startTime']}</b> da <b>{escape(settings.center_address)}</b>ga kelishingiz kerak.")
    else:
        when = "Dars vaqti haqida o'qituvchi siz bilan bog'lanadi."
    return (
        f"✅ «{escape(d['courseTitle'])}» kursiga qo'shilish so'rovingizni o'qituvchi ma'qulladi!\n\n"
        f"{when}\n\n{TERMS}"
    )