import logging
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy import select
from bot.database import AsyncSessionLocal
from bot.models import User
from bot.keyboards import get_currency_keyboard, get_main_menu_reply_keyboard
from bot.i18n import get_text
from bot.handlers.admin import is_admin

logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    user_lang = message.from_user.language_code

    # Fallback to supported language or default 'ru'
    init_lang = "ru"
    if user_lang in ["ru", "uz", "tj", "en"]:
        init_lang = user_lang

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                base_currency="TJS",
                language=init_lang
            )
            session.add(user)
            await session.commit()
            logger.info(f"Registered new user telegram_id={telegram_id} with lang={init_lang}")

        lang = user.language if user else init_lang
        base_currency = user.base_currency if user else "TJS"

    welcome_text = get_text(
        "start_welcome",
        lang=lang,
        first_name=message.from_user.first_name,
        base_currency=base_currency
    )

    await message.answer(
        text=welcome_text,
        reply_markup=get_currency_keyboard(),
        parse_mode="Markdown"
    )
    await message.answer(
        get_text("menu_open", lang=lang),
        reply_markup=get_main_menu_reply_keyboard(
            lang=lang,
            is_admin=is_admin(telegram_id),
        )
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        lang = user.language if user else "ru"

    help_text = get_text("help_text", lang=lang)
    await message.answer(help_text, parse_mode="Markdown")
