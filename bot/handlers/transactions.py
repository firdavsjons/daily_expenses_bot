import logging
import uuid
from datetime import datetime, timezone
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from bot.database import AsyncSessionLocal
from bot.models import User, Category, Transaction, Budget, LearnedKeyword, utc_now
from bot.parser import extract_learning_keywords, parse_transaction_message, ParsedTransaction
from bot.services.currency_service import get_latest_exchange_rate
from bot.keyboards import get_category_selection_keyboard, get_undo_keyboard
from bot.i18n import get_text, DICTIONARIES
from bot.i18n.categories import get_category_name

logger = logging.getLogger(__name__)
router = Router()

# Collect all reply keyboard button texts across all languages to ignore them in free text parser
ALL_MENU_BUTTON_TEXTS = set()
for lang_dict in DICTIONARIES.values():
    for key in ["btn_today", "btn_month", "btn_rates", "btn_categories", "btn_currency", "btn_recurring", "btn_language"]:
        btn_text = lang_dict.get(key)
        if btn_text:
            ALL_MENU_BUTTON_TEXTS.add(btn_text)

# In-memory storage for pending transactions awaiting category choice
PENDING_TRANSACTIONS = {}

async def process_parsed_transaction(message: Message, user: User, parsed: ParsedTransaction, session):
    """
    Saves transaction and checks budget limits.
    """
    lang = user.language if user.language else "ru"

    # Fetch latest exchange rate to base currency
    rate = await get_latest_exchange_rate(session, parsed.currency, user.base_currency)
    amount_base = round(parsed.amount * rate, 2)

    # Resolve category in DB
    category = None
    if parsed.category_id:
        cat_stmt = select(Category).where(Category.id == parsed.category_id)
        cat_res = await session.execute(cat_stmt)
        category = cat_res.scalar_one_or_none()

    if not category:
        cat_stmt = select(Category).where(Category.name == parsed.category_name)
        cat_res = await session.execute(cat_stmt)
        category = cat_res.scalar_one_or_none()

    if not category:
        cat_stmt = select(Category).where(Category.is_default == True, Category.type == parsed.type).limit(1)
        cat_res = await session.execute(cat_stmt)
        category = cat_res.scalar_one_or_none()

    now = utc_now()
    tx = Transaction(
        user_id=user.id,
        category_id=category.id if category else 1,
        amount=parsed.amount,
        currency=parsed.currency,
        amount_base=amount_base,
        exchange_rate=rate,
        raw_text=parsed.raw_text,
        comment=parsed.comment,
        type=parsed.type,
        occurred_at=now,
        created_at=now
    )
    session.add(tx)
    await session.commit()

    type_title = get_text("tx_added_income" if parsed.type == "income" else "tx_added_expense", lang=lang)
    cat_icon = category.icon if (category and category.icon) else "📁"
    cat_name = get_category_name(category.name if category else "Разное", lang)

    rate_msg = f" (rate: {rate:.4f})" if parsed.currency != user.base_currency else ""
    amount_line = get_text("tx_amount_label", lang=lang, amount=parsed.amount, currency=parsed.currency, amount_base=amount_base, base_currency=user.base_currency, rate_msg=rate_msg)
    cat_line = get_text("tx_category_label", lang=lang, icon=cat_icon, category=cat_name)
    comment_line = get_text("tx_comment_label", lang=lang, comment=parsed.comment)

    response_text = f"{type_title}\n\n{amount_line}\n{cat_line}\n{comment_line}"
    await message.answer(
        response_text,
        reply_markup=get_undo_keyboard(tx.id, lang),
        parse_mode="Markdown"
    )

    # Check monthly budget if it's an expense
    if parsed.type == "expense" and category:
        await check_budget_limit(message, user, category, session)

async def check_budget_limit(message: Message, user: User, category: Category, session):
    """
    Checks if expense exceeds 80% or 100% of category monthly budget.
    """
    lang = user.language if user.language else "ru"
    budget_stmt = select(Budget).where(Budget.user_id == user.id, Budget.category_id == category.id)
    budget_res = await session.execute(budget_stmt)
    budget = budget_res.scalar_one_or_none()

    if not budget:
        return

    now = utc_now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    spent_stmt = (
        select(func.sum(Transaction.amount_base))
        .where(
            Transaction.user_id == user.id,
            Transaction.category_id == category.id,
            Transaction.type == "expense",
            Transaction.occurred_at >= month_start
        )
    )
    spent_res = await session.execute(spent_stmt)
    total_spent_base = float(spent_res.scalar() or 0.0)

    budget_rate = await get_latest_exchange_rate(session, budget.currency, user.base_currency)
    limit_base = float(budget.monthly_limit) * budget_rate
    percent_spent = (total_spent_base / limit_base * 100) if limit_base > 0 else 0

    loc_cat = get_category_name(category.name, lang)
    icon = category.icon or "📁"

    if percent_spent >= 100:
        await message.answer(
            get_text("budget_exceeded", lang=lang, icon=icon, category=loc_cat, spent=total_spent_base, limit=limit_base, currency=user.base_currency, percent=percent_spent),
            parse_mode="Markdown"
        )
    elif percent_spent >= budget.notify_at_percent:
        await message.answer(
            get_text("budget_warning", lang=lang, icon=icon, category=loc_cat, spent=total_spent_base, limit=limit_base, currency=user.base_currency, percent=percent_spent),
            parse_mode="Markdown"
        )

@router.message(Command("add"))
async def cmd_add(message: Message):
    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.telegram_id == message.from_user.id)
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        lang = user.language if user else "ru"

        logger.info(f"Command /add received from user {message.from_user.id}: '{message.text}'")
        text_args = message.text.partition(" ")[2].strip()
        if not text_args:
            await message.answer(get_text("cmd_add_usage", lang=lang), parse_mode="Markdown")
            return
        try:
            await handle_transaction_text(message, text_args)
        except Exception as e:
            logger.exception(f"Error executing /add command: {e}")
            await message.answer("⚠️ Error processing transaction.")

@router.message(F.text & ~F.text.startswith("/"))
async def handle_free_text(message: Message):
    logger.info(f"Free text received from user {message.from_user.id}: '{message.text}'")
    if message.text in ALL_MENU_BUTTON_TEXTS:
        return
    try:
        await handle_transaction_text(message, message.text)
    except Exception as e:
        logger.exception(f"Error processing free text transaction '{message.text}': {e}")
        await message.answer("⚠️ Error processing message.")

async def handle_transaction_text(message: Message, text: str):
    logger.info(f"Processing transaction parsing for text: '{text}'")
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()

        if not user:
            user = User(telegram_id=message.from_user.id, username=message.from_user.username, base_currency="TJS", language="ru")
            session.add(user)
            await session.commit()

        lang = user.language if user else "ru"

        cat_stmt = select(Category).where((Category.user_id == user.id) | (Category.is_default == True))
        cat_res = await session.execute(cat_stmt)
        categories = cat_res.scalars().all()

        cat_dicts = [
            {
                "id": c.id,
                "name": c.name,
                "type": c.type,
                "icon": c.icon,
                "keywords": c.keywords or []
            }
            for c in categories
        ]

        learned_stmt = (
            select(LearnedKeyword.keyword, LearnedKeyword.category_id, Category.name)
            .join(Category, Category.id == LearnedKeyword.category_id)
            .where(LearnedKeyword.user_id == user.id)
        )
        learned_res = await session.execute(learned_stmt)
        learned_keywords = [
            {"keyword": keyword, "category_id": category_id, "category_name": category_name}
            for keyword, category_id, category_name in learned_res.all()
        ]

        parsed = parse_transaction_message(text, cat_dicts, user.base_currency, learned_keywords)
        logger.info(f"Parsed result for '{text}': {parsed}")

        if not parsed:
            await message.answer(get_text("parse_error_amount", lang=lang), parse_mode="Markdown")
            return

        if parsed.category_name == "Разное":
            pending_id = str(uuid.uuid4())[:8]
            PENDING_TRANSACTIONS[pending_id] = {
                "user_id": user.id,
                "parsed": parsed,
                "source_text": text,
            }

            kb = get_category_selection_keyboard(categories, pending_id, lang=lang)
            await message.answer(
                get_text("parse_confirm_category", lang=lang, amount=parsed.amount, currency=parsed.currency),
                reply_markup=kb,
                parse_mode="Markdown"
            )
            return

        await process_parsed_transaction(message, user, parsed, session)

@router.callback_query(F.data.startswith("select_cat:"))
async def cb_select_category(callback: CallbackQuery):
    _, pending_id, cat_id_str = callback.data.split(":")
    cat_id = int(cat_id_str)

    pending = PENDING_TRANSACTIONS.pop(pending_id, None)
    if not pending:
        await callback.answer("Selection expired.", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        user_stmt = select(User).where(User.id == pending["user_id"])
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()

        parsed: ParsedTransaction = pending["parsed"]
        parsed.category_id = cat_id

        cat_stmt = select(Category).where(Category.id == cat_id)
        cat_res = await session.execute(cat_stmt)
        cat = cat_res.scalar_one_or_none()
        if cat:
            parsed.category_name = cat.name
            parsed.type = cat.type

            for keyword in extract_learning_keywords(pending["source_text"]):
                exists_stmt = select(LearnedKeyword).where(
                    LearnedKeyword.user_id == user.id,
                    LearnedKeyword.keyword == keyword,
                )
                exists_res = await session.execute(exists_stmt)
                if not exists_res.scalar_one_or_none():
                    session.add(LearnedKeyword(user_id=user.id, keyword=keyword, category_id=cat.id))
            await session.commit()

        await callback.message.delete()
        await process_parsed_transaction(callback.message, user, parsed, session)
        await callback.answer()
