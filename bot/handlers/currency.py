import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from bot.database import AsyncSessionLocal
from bot.models import User
from bot.keyboards import get_currency_keyboard, get_language_keyboard, get_main_menu_reply_keyboard
from bot.handlers.admin import is_admin
from bot.services.currency_service import get_latest_exchange_rate
from bot.i18n import get_text, DICTIONARIES

logger = logging.getLogger(__name__)
router = Router()

# Collect all language button texts across dictionaries for button matching
LANG_BUTTON_TEXTS = [dict_data.get("btn_language") for dict_data in DICTIONARIES.values() if dict_data.get("btn_language")]
CURR_BUTTON_TEXTS = [dict_data.get("btn_currency") for dict_data in DICTIONARIES.values() if dict_data.get("btn_currency")]
RATES_BUTTON_TEXTS = [dict_data.get("btn_rates") for dict_data in DICTIONARIES.values() if dict_data.get("btn_rates")]

@router.message(Command("language"))
@router.message(F.text.in_(LANG_BUTTON_TEXTS))
async def cmd_language(message: Message):
    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == message.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()

        lang = user.language if user else "ru"

    title_text = get_text("lang_choose_title", lang=lang)
    await message.answer(title_text, reply_markup=get_language_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data.startswith("set_lang_"))
async def cb_set_language(callback: CallbackQuery):
    new_lang = callback.data.replace("set_lang_", "").lower()
    if new_lang not in ["ru", "uz", "tj", "en"]:
        await callback.answer("Unsupported language", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == callback.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()

        if user:
            user.language = new_lang
            await session.commit()

    changed_msg = get_text("lang_changed", lang=new_lang)
    await callback.message.edit_text(changed_msg, parse_mode="Markdown")
    await callback.message.answer(
        get_text("menu_open", lang=new_lang),
        reply_markup=get_main_menu_reply_keyboard(
            lang=new_lang,
            is_admin=is_admin(callback.from_user.id),
        )
    )
    await callback.answer()

@router.message(Command("currency"))
@router.message(F.text.in_(CURR_BUTTON_TEXTS))
async def cmd_currency(message: Message):
    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == message.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()

        curr = user.base_currency if user else "TJS"
        lang = user.language if user else "ru"

        msg_text = get_text("curr_current", lang=lang, currency=curr)
        await message.answer(msg_text, reply_markup=get_currency_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data.startswith("set_currency_"))
async def cb_set_currency(callback: CallbackQuery):
    new_curr = callback.data.replace("set_currency_", "")
    if new_curr not in ["TJS", "RUB", "USD"]:
        await callback.answer("Invalid currency", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == callback.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()

        if user:
            user.base_currency = new_curr
            await session.commit()
            lang = user.language
        else:
            lang = "ru"

    msg_text = get_text("curr_changed", lang=lang, currency=new_curr)
    await callback.message.edit_text(msg_text, parse_mode="Markdown")
    await callback.answer()

@router.message(Command("rates"))
@router.message(F.text.in_(RATES_BUTTON_TEXTS))
async def cmd_rates(message: Message):
    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == message.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        lang = user.language if user else "ru"

        usd_rate = await get_latest_exchange_rate(session, "USD", "TJS")
        rub_rate = await get_latest_exchange_rate(session, "RUB", "TJS")

        text = get_text("rates_title", lang=lang, usd=usd_rate, rub=rub_rate)
        await message.answer(text, parse_mode="Markdown")
