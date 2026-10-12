import logging
from datetime import datetime, timedelta, timezone
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.database import AsyncSessionLocal
from bot.models import User, Category, RecurringPayment, utc_now
from bot.i18n import get_text, DICTIONARIES
from bot.i18n.categories import get_category_name

logger = logging.getLogger(__name__)
router = Router()

REC_BUTTON_TEXTS = [dict_data.get("btn_recurring") for dict_data in DICTIONARIES.values() if dict_data.get("btn_recurring")]

@router.message(Command("recurring"))
@router.message(F.text.in_(REC_BUTTON_TEXTS))
async def cmd_recurring(message: Message):
    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == message.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()

        if not user:
            await message.answer("Please send /start to register.")
            return

        lang = user.language if user else "ru"
        stmt = (
            select(RecurringPayment)
            .options(selectinload(RecurringPayment.category))
            .where(RecurringPayment.user_id == user.id, RecurringPayment.is_active == True)
        )
        res = await session.execute(stmt)
        payments = res.scalars().all()

        if not payments:
            await message.answer(get_text("rec_empty", lang=lang), parse_mode="Markdown")
            return

        lines = [get_text("rec_header", lang=lang)]
        freq_map = {
            "daily": {"ru": "ежедневно", "uz": "har kuni", "tj": "ҳар рӯз", "en": "daily"},
            "weekly": {"ru": "еженедельно", "uz": "har ҳафта", "tj": "ҳар ҳафта", "en": "weekly"},
            "monthly": {"ru": "ежемесячно", "uz": "har oy", "tj": "ҳар моҳ", "en": "monthly"}
        }

        for p in payments:
            cat_name = get_category_name(p.category.name if p.category else "Разное", lang)
            cat_icon = p.category.icon if (p.category and p.category.icon) else "📁"
            freq_str = freq_map.get(p.frequency, {}).get(lang, p.frequency)
            next_run = p.next_run_at.strftime("%d.%m.%Y %H:%M")
            lines.append(
                f"• {cat_icon} *{cat_name}*: `{p.amount} {p.currency}` ({freq_str})\n"
                f"  📝 {p.comment or '-'} | 🕒 Next: {next_run}"
            )

        await message.answer("\n".join(lines), parse_mode="Markdown")

@router.message(Command("addrecurring"))
async def cmd_addrecurring(message: Message):
    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == message.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        lang = user.language if user else "ru"

        parts = message.text.split(maxsplit=5)
        if len(parts) < 5:
            await message.answer(get_text("rec_add_usage", lang=lang), parse_mode="Markdown")
            return

        cat_input = parts[1].strip()
        try:
            amount_val = float(parts[2].strip().replace(',', '.'))
        except ValueError:
            await message.answer(get_text("budget_invalid_amount", lang=lang), parse_mode="Markdown")
            return

        curr_val = parts[3].strip().upper()
        freq_val = parts[4].strip().lower()
        comment_val = parts[5].strip() if len(parts) > 5 else "Recurring payment"

        if curr_val not in ["TJS", "RUB", "USD"]:
            await message.answer(get_text("budget_invalid_currency", lang=lang), parse_mode="Markdown")
            return

        if freq_val not in ["daily", "weekly", "monthly"]:
            await message.answer(get_text("rec_freq_error", lang=lang), parse_mode="Markdown")
            return

        if not user:
            await message.answer("Please send /start to register.")
            return

        cat_stmt = select(Category).where(
            ((Category.user_id == user.id) | (Category.is_default == True)),
            Category.name.ilike(cat_input)
        )
        cat_res = await session.execute(cat_stmt)
        category = cat_res.scalar_one_or_none()

        if not category:
            await message.answer(get_text("budget_cat_not_found", lang=lang, category=cat_input), parse_mode="Markdown")
            return

        now = utc_now()
        if freq_val == "daily":
            next_run = now + timedelta(days=1)
        elif freq_val == "weekly":
            next_run = now + timedelta(weeks=1)
        else:
            next_run = now + timedelta(days=30)

        rec_payment = RecurringPayment(
            user_id=user.id,
            category_id=category.id,
            amount=amount_val,
            currency=curr_val,
            comment=comment_val,
            frequency=freq_val,
            next_run_at=next_run,
            is_active=True
        )
        session.add(rec_payment)
        await session.commit()

        loc_cat_name = get_category_name(category.name, lang)
        await message.answer(
            get_text(
                "rec_added_success",
                lang=lang,
                icon=category.icon or "📁",
                category=loc_cat_name,
                amount=amount_val,
                currency=curr_val,
                frequency=freq_val,
                next_run=next_run.strftime('%d.%m.%Y %H:%M')
            ),
            parse_mode="Markdown"
        )
