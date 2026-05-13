import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8625557628:AAHeUC2WxfMjJk-RRq3IxTtUJoc0H4XSsAM")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7758296066"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot_database.db")

# Document styles
DOC_STYLES = {
    "apa": "APA Style",
    "harvard": "Harvard Style",
    "uzbek": "O'zbek Standarti"
}

# Document types
DOC_TYPES = {
    "referat": "Referat (Essay)",
    "kurs": "Kurs Ishi (Coursework)",
    "maqola": "Maqola (Article)",
    "slide": "Slide Presentation"
}

# Pricing
FIRST_DOC_PRICE = 0
NEXT_DOC_PRICE_UZS = 2000
NEXT_DOC_PRICE_USD = 0.17
