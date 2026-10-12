import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from bot.database import AsyncSessionLocal
from bot.models import User, Category, Budget
from bot.i18n import get_text
from bot.i18n.categories import get_category_name

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("setbudget"))
async def cmd_setbudget(message: Message):
    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == message.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        lang = user.language if user else "ru"

        args = message.text.split(maxsplit=3)
        if len(args) < 4:
            await message.answer(get_text("budget_set_usage", lang=lang), parse_mode="Markdown")
            return

        cat_input = args[1].strip()
        try:
            limit_val = float(args[2].strip().replace(',', '.'))
        except ValueError:
            await message.answer(get_text("budget_invalid_amount", lang=lang), parse_mode="Markdown")
            return

        currency_val = args[3].strip().upper()
        if currency_val not in ["TJS", "RUB", "USD"]:
            await message.answer(get_text("budget_invalid_currency", lang=lang), parse_mode="Markdown")
            return

        if not user:
            await message.answer("Please send /start to register.")
            return

        # Find category
        cat_stmt = select(Category).where(
            ((Category.user_id == user.id) | (Category.is_default == True)),
            Category.name.ilike(cat_input)
        )
        cat_res = await session.execute(cat_stmt)
        category = cat_res.scalar_one_or_none()

        if not category:
            await message.answer(get_text("budget_cat_not_found", lang=lang, category=cat_input), parse_mode="Markdown")
            return

        # Check existing budget
        budget_stmt = select(Budget).where(Budget.user_id == user.id, Budget.category_id == category.id)
        budget_res = await session.execute(budget_stmt)
        budget = budget_res.scalar_one_or_none()

        if not budget:
            budget = Budget(
                user_id=user.id,
                category_id=category.id,
                monthly_limit=limit_val,
                currency=currency_val,
                notify_at_percent=80
            )
            session.add(budget)
        else:
            budget.monthly_limit = limit_val
            budget.currency = currency_val

        await session.commit()

        loc_cat_name = get_category_name(category.name, lang)
        await message.answer(
            get_text("budget_set_success", lang=lang, category=loc_cat_name, limit=limit_val, currency=currency_val),
            parse_mode="Markdown"
        )
