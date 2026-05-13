import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import BotCommand, Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from config import BOT_TOKEN, ADMIN_ID
from database import init_db, get_session, User, Document
from keyboards.main_kb import main_menu, style_menu, finish_menu
from services.document_generator import DocumentGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentStates(StatesGroup):
    choosing_type = State()
    choosing_style = State()
    writing_title = State()
    writing_content = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
doc_gen = DocumentGenerator()

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    session = get_session()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    
    if not user:
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username or "unknown",
            first_name=message.from_user.first_name or "User",
            created_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        logger.info(f"✅ New user: {message.from_user.id}")
    
    welcome = """
🎓 **Akademik Yordamchi Botga Xush Kelibsiz!**

Siz quyidagi hujjatlarni yarata olasiz:
📝 **Referat** - Kichik tadqiqot
📚 **Kurs Ishi** - Kurs oxiri
📄 **Maqola** - Ilmiy maqola
🎯 **Slide** - Prezentasiya

💡 **Birinchi hujjat TEKIN!**
Keyingilari 2,000 UZS

Qanday hujjat yaratmoqchisiz?
    """
    
    await message.answer(welcome, reply_markup=main_menu())
    session.close()
    await state.clear()

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
📖 **Qo'llanma:**

1. Hujjat turini tanlang
2. Uslubni tanlang (APA/Harvard/Uzbek)
3. Sarlavha yuboring
4. Matnni yuboring
5. PDF olasiz!

Birinchi hujjat TEKIN!
    """
    await message.answer(help_text, reply_markup=main_menu())

@dp.callback_query(F.data.startswith("doc_"))
async def process_doc_type(callback: CallbackQuery, state: FSMContext):
    doc_type = callback.data.replace("doc_", "")
    
    doc_types = {
        "referat": "📝 Referat",
        "kurs": "📚 Kurs Ishi",
        "maqola": "📄 Maqola",
        "slide": "🎯 Slide"
    }
    
    if doc_type not in doc_types:
        await callback.answer("❌ Noto'g'ri tur!")
        return
    
    await state.update_data(doc_type=doc_type)
    await callback.message.edit_text(
        f"✅ Siz {doc_types[doc_type]} turini tanladingiz\n\n"
        "📋 Endi uslubni tanlang:",
        reply_markup=style_menu()
    )
    await state.set_state(DocumentStates.choosing_style)
    await callback.answer()

@dp.callback_query(F.data.startswith("style_"))
async def process_style(callback: CallbackQuery, state: FSMContext):
    style = callback.data.replace("style_", "")
    
    styles = {
        "apa": "APA Style",
        "harvard": "Harvard Style",
        "uzbek": "O'zbek Standarti"
    }
    
    if style not in styles:
        await callback.answer("❌ Noto'g'ri uslub!")
        return
    
    await state.update_data(style=style)
    await callback.message.edit_text(
        f"✅ Siz {styles[style]} ni tanladingiz\n\n"
        "✏️ Endi hujjatning **sarlavhasini** yuboring:"
    )
    await state.set_state(DocumentStates.writing_title)
    await callback.answer()

@dp.message(DocumentStates.writing_title)
async def process_title(message: Message, state: FSMContext):
    if len(message.text) < 3 or len(message.text) > 200:
        await message.answer("❌ Sarlavha 3 dan 200 ta belgigacha bo'lishi kerak!")
        return
    
    await state.update_data(title=message.text)
    await message.answer(
        f"✅ Sarlavha: **{message.text}**\n\n"
        "📝 Endi **matnni** yuboring:"
    )
    await state.set_state(DocumentStates.writing_content)

@dp.message(DocumentStates.writing_content)
async def process_content(message: Message, state: FSMContext):
    data = await state.get_data()
    
    if "content" in data:
        data["content"] += "\n\n" + message.text
    else:
        data["content"] = message.text
    
    await state.update_data(content=data["content"])
    
    await message.answer(
        "✅ Matn qabul qilindi!\n\n"
        f"📊 Hajmi: {len(data['content'])} belgi\n\n"
        "🔄 Yana matn qo'shib olasiz yoki tugatishingiz mumkin.",
        reply_markup=finish_menu()
    )

@dp.callback_query(F.data == "finish_doc")
async def finish_document(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("⏳ Hujjat yaratilmoqda...", reply_markup=None)
    
    data = await state.get_data()
    session = get_session()
    
    try:
        doc_path = doc_gen.generate_document(
            doc_type=data['doc_type'],
            style=data['style'],
            title=data['title'],
            content=data['content'],
            user_id=callback.from_user.id
        )
        
        document = Document(
            user_id=callback.from_user.id,
            doc_type=data['doc_type'],
            template_style=data['style'],
            title=data['title'],
            content=data['content'],
            file_path=doc_path,
            created_at=datetime.utcnow()
        )
        
        user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
        if user:
            user.first_doc_used = True
        
        session.add(document)
        session.commit()
        
        logger.info(f"✅ Document created: {callback.from_user.id}")
        
        with open(doc_path, 'rb') as file:
            await callback.message.answer_document(
                file,
                caption=f"✅ Hujjat tayyorlandi!\n\n"
                        f"📝 Tur: {data['doc_type']}\n"
                        f"📋 Uslub: {data['style']}\n"
                        f"📖 Sarlavha: {data['title']}"
            )
        
        await state.clear()
        await callback.message.answer(
            "🎉 Boshqa hujjat yaratmoqchimisiz?",
            reply_markup=main_menu()
        )
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await callback.message.answer(f"❌ Xatolik: {str(e)}", reply_markup=main_menu())
    finally:
        session.close()

@dp.message()
async def echo(message: Message):
    await message.answer(
        "❓ Tushunmadim!\n/start - Botni boshlash\n/help - Yordam",
        reply_markup=main_menu()
    )

async def main():
    logger.info("🚀 Bot ishga tushmoqda...")
    logger.info(f"📋 Admin ID: {ADMIN_ID}")
    
    init_db()
    logger.info("✅ Database tayyorlandi")
    
    commands = [
        BotCommand(command="start", description="Botni boshlash"),
        BotCommand(command="help", description="Yordam"),
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Bot buyruqlari o'rnatildi")
    
    try:
        logger.info("✅ Bot ishga tushdi!")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"❌ Bot xatosi: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Bot to'xtatildi")
