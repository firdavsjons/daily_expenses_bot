from datetime import timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from bot.database import AsyncSessionLocal
from bot.i18n import get_text
from bot.i18n.categories import get_category_name
from bot.keyboards import get_undo_confirmation_keyboard, get_undo_keyboard
from bot.models import Transaction, User, utc_now

router = Router()
UNDO_WINDOW = timedelta(minutes=10)


def _is_recent(transaction: Transaction) -> bool:
    occurred_at = transaction.occurred_at
    if occurred_at.tzinfo is None:
        occurred_at = occurred_at.replace(tzinfo=utc_now().tzinfo)
    return occurred_at >= utc_now() - UNDO_WINDOW


def _transaction_description(transaction: Transaction, lang: str) -> str:
    category = transaction.category
    category_name = get_category_name(category.name, lang) if category else get_text("undo_unknown_category", lang)
    icon = category.icon if category and category.icon else "📁"
    return get_text(
        "undo_transaction_details",
        lang,
        amount=transaction.amount,
        currency=transaction.currency,
        icon=icon,
        category=category_name,
    )


async def _get_user(session, telegram_id: int):
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def _get_owned_transaction(session, transaction_id: int, telegram_id: int):
    user = await _get_user(session, telegram_id)
    if not user:
        return None, None
    result = await session.execute(
        select(Transaction)
        .options(selectinload(Transaction.category))
        .where(Transaction.id == transaction_id, Transaction.user_id == user.id)
    )
    return user, result.scalar_one_or_none()


async def _delete_transaction(session, transaction_id: int, telegram_id: int):
    user, transaction = await _get_owned_transaction(session, transaction_id, telegram_id)
    if not transaction:
        return user, None
    if not _is_recent(transaction):
        return user, False
    await session.execute(delete(Transaction).where(Transaction.id == transaction.id, Transaction.user_id == user.id))
    await session.commit()
    return user, True


@router.message(Command("undo"))
async def cmd_undo(message: Message):
    async with AsyncSessionLocal() as session:
        user = await _get_user(session, message.from_user.id)
        lang = user.language if user else "ru"
        if not user:
            await message.answer(get_text("undo_nothing", lang))
            return

        result = await session.execute(
            select(Transaction)
            .options(selectinload(Transaction.category))
            .where(Transaction.user_id == user.id)
            .order_by(Transaction.occurred_at.desc(), Transaction.created_at.desc())
            .limit(1)
        )
        transaction = result.scalar_one_or_none()
        if not transaction:
            await message.answer(get_text("undo_nothing", lang))
            return
        if not _is_recent(transaction):
            await message.answer(get_text("undo_expired", lang))
            return

        description = _transaction_description(transaction, lang)
        await message.answer(
            get_text("undo_confirm_prompt", lang, details=description),
            reply_markup=get_undo_confirmation_keyboard(transaction.id, lang),
            parse_mode="Markdown"
        )


@router.callback_query(F.data.startswith("undo:"))
async def cb_undo(callback: CallbackQuery):
    transaction_id = int(callback.data.split(":", 1)[1])
    async with AsyncSessionLocal() as session:
        user, transaction = await _get_owned_transaction(session, transaction_id, callback.from_user.id)
        lang = user.language if user else "ru"
        if transaction is None:
            await callback.answer(get_text("undo_unavailable", lang), show_alert=True)
            return
        if not _is_recent(transaction):
            await callback.answer(get_text("undo_expired", lang), show_alert=True)
            return
        await session.execute(delete(Transaction).where(Transaction.id == transaction.id, Transaction.user_id == user.id))
        await session.commit()
        await callback.message.edit_text(get_text("undo_done", lang), reply_markup=None)
        await callback.answer()


@router.callback_query(F.data.startswith("undo_confirm:"))
async def cb_undo_confirm(callback: CallbackQuery):
    transaction_id = int(callback.data.split(":", 1)[1])
    async with AsyncSessionLocal() as session:
        user, deleted = await _delete_transaction(session, transaction_id, callback.from_user.id)
        lang = user.language if user else "ru"
        if deleted is False:
            await callback.answer(get_text("undo_expired", lang), show_alert=True)
            return
        if deleted is None:
            await callback.answer(get_text("undo_unavailable", lang), show_alert=True)
            return
        await callback.message.edit_text(get_text("undo_done", lang), reply_markup=None)
        await callback.answer()


@router.callback_query(F.data.startswith("undo_cancel:"))
async def cb_undo_cancel(callback: CallbackQuery):
    transaction_id = int(callback.data.split(":", 1)[1])
    async with AsyncSessionLocal() as session:
        user, transaction = await _get_owned_transaction(session, transaction_id, callback.from_user.id)
        lang = user.language if user else "ru"
        if transaction is None:
            await callback.answer(get_text("undo_unavailable", lang), show_alert=True)
            return
        await callback.message.edit_text(
            get_text("undo_kept", lang),
            reply_markup=get_undo_keyboard(transaction.id, lang)
        )
        await callback.answer()