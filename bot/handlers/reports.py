import logging
from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from sqlalchemy import select

from bot.database import AsyncSessionLocal
from bot.models import User
from bot.services.report_service import get_period_dates, generate_period_report, export_transactions_to_excel
from bot.i18n import get_text, DICTIONARIES

logger = logging.getLogger(__name__)
router = Router()

TODAY_BUTTON_TEXTS = [dict_data.get("btn_today") for dict_data in DICTIONARIES.values() if dict_data.get("btn_today")]
MONTH_BUTTON_TEXTS = [dict_data.get("btn_month") for dict_data in DICTIONARIES.values() if dict_data.get("btn_month")]

@router.message(Command("today"))
@router.message(F.text.in_(TODAY_BUTTON_TEXTS))
async def cmd_today(message: Message):
    await send_period_report(message, "today")

@router.message(Command("week"))
async def cmd_week(message: Message):
    await send_period_report(message, "week")

@router.message(Command("month"))
@router.message(F.text.in_(MONTH_BUTTON_TEXTS))
async def cmd_month(message: Message):
    await send_period_report(message, "month")

async def send_period_report(message: Message, period_name: str):
    start, end = get_period_dates(period_name)
    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == message.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()

        if not user:
            await message.answer("Please send /start to register.")
            return

        text_msg, chart_bytes = await generate_period_report(session, user, start, end)

        if chart_bytes:
            photo = BufferedInputFile(chart_bytes, filename=f"report_{period_name}.png")
            await message.answer_photo(photo=photo, caption=text_msg, parse_mode="Markdown")
        else:
            await message.answer(text_msg, parse_mode="Markdown")

@router.message(Command("report"))
async def cmd_custom_report(message: Message):
    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == message.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        lang = user.language if user else "ru"

        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.answer(get_text("report_custom_usage", lang=lang), parse_mode="Markdown")
            return

        try:
            start_date = datetime.strptime(args[1].strip(), "%d.%m.%Y").replace(tzinfo=timezone.utc)
            end_date = datetime.strptime(args[2].strip(), "%d.%m.%Y").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        except ValueError:
            await message.answer(get_text("report_date_format_error", lang=lang), parse_mode="Markdown")
            return

        if not user:
            await message.answer("Please send /start to register.")
            return

        text_msg, chart_bytes = await generate_period_report(session, user, start_date, end_date)

        if chart_bytes:
            photo = BufferedInputFile(chart_bytes, filename="custom_report.png")
            await message.answer_photo(photo=photo, caption=text_msg, parse_mode="Markdown")
        else:
            await message.answer(text_msg, parse_mode="Markdown")

@router.message(Command("export"))
async def cmd_export(message: Message):
    now = datetime.now(timezone.utc)
    start_date = datetime(2020, 1, 1, tzinfo=timezone.utc)

    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == message.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()

        if not user:
            await message.answer("Please send /start to register.")
            return

        lang = user.language if user else "ru"
        excel_bytes = await export_transactions_to_excel(session, user, start_date, now)
        file_doc = BufferedInputFile(excel_bytes, filename=f"expenses_export_{now.strftime('%Y%m%d')}.xlsx")

        await message.answer_document(
            document=file_doc,
            caption=get_text("export_caption", lang=lang),
            parse_mode="Markdown"
        )
