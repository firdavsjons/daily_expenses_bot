import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from bot.database import AsyncSessionLocal
from bot.models import User, Category
from bot.i18n import get_text, DICTIONARIES
from bot.i18n.categories import get_category_name

logger = logging.getLogger(__name__)
router = Router()

CAT_BUTTON_TEXTS = [dict_data.get("btn_categories") for dict_data in DICTIONARIES.values() if dict_data.get("btn_categories")]

@router.message(Command("categories"))
@router.message(F.text.in_(CAT_BUTTON_TEXTS))
async def cmd_categories(message: Message):
    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == message.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()

        user_id = user.id if user else None
        lang = user.language if user else "ru"

        stmt = select(Category).where((Category.user_id == user_id) | (Category.is_default == True))
        result = await session.execute(stmt)
        categories = result.scalars().all()

        expenses = [c for c in categories if c.type == "expense"]
        incomes = [c for c in categories if c.type == "income"]

        exp_lines = [f"{c.icon or '📁'} *{get_category_name(c.name, lang)}*" for c in expenses]
        inc_lines = [f"{c.icon or '💰'} *{get_category_name(c.name, lang)}*" for c in incomes]

        text = get_text(
            "cat_list_header",
            lang=lang,
            expenses=("\n".join(exp_lines) if exp_lines else "-"),
            incomes=("\n".join(inc_lines) if inc_lines else "-")
        )

        await message.answer(text, parse_mode="Markdown")

@router.message(Command("addcategory"))
async def cmd_addcategory(message: Message):
    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == message.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        lang = user.language if user else "ru"

        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.answer(get_text("cat_add_usage", lang=lang), parse_mode="Markdown")
            return

        cat_name = args[1].strip()
        cat_type = args[2].strip().lower()

        if cat_type not in ["expense", "income"]:
            await message.answer(get_text("cat_type_error", lang=lang), parse_mode="Markdown")
            return

        if not user:
            user = User(telegram_id=message.from_user.id, username=message.from_user.username, language=lang)
            session.add(user)
            await session.commit()

        icon = "🟢" if cat_type == "income" else "🔴"
        new_cat = Category(
            user_id=user.id,
            name=cat_name,
            type=cat_type,
            keywords=[cat_name.lower()],
            icon=icon,
            is_default=False
        )
        session.add(new_cat)
        await session.commit()

        type_title = "Income" if cat_type == "income" else "Expense"
        await message.answer(
            get_text("cat_added_success", lang=lang, name=cat_name, type_title=type_title),
            parse_mode="Markdown"
        )
