from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    """Main menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Referat", callback_data="doc_referat")],
        [InlineKeyboardButton(text="📚 Kurs Ishi", callback_data="doc_kurs")],
        [InlineKeyboardButton(text="📄 Maqola", callback_data="doc_maqola")],
        [InlineKeyboardButton(text="🎯 Slide", callback_data="doc_slide")],
    ])

def style_menu():
    """Style selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 APA Style", callback_data="style_apa")],
        [InlineKeyboardButton(text="🎯 Harvard Style", callback_data="style_harvard")],
        [InlineKeyboardButton(text="🎯 O'zbek Standarti", callback_data="style_uzbek")],
    ])

def finish_menu():
    """Finish document menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tugatish va PDF Olish", callback_data="finish_doc")],
        [InlineKeyboardButton(text="➕ Yana Matn Qo'shish", callback_data="add_more")],
    ])
