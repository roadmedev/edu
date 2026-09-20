import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi - .env faylini tekshiring")
