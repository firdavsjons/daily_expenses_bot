import html
import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import case, func, select, text

from bot import config
from bot.database import AsyncSessionLocal
from bot.keyboards import get_main_menu_reply_keyboard
from bot.models import Base, Budget, Category, ExchangeRate, RecurringPayment, Transaction, User
from bot.services.scheduler import scheduler

logger = logging.getLogger(__name__)
router = Router()
LOG_FILE = Path(__file__).resolve().parents[2] / "logs" / "bot.log"
USERS_PER_PAGE = 8
MAX_MESSAGE_LENGTH = 3900


def is_admin(telegram_id: int) -> bool:
    return telegram_id == config.ADMIN_TELEGRAM_ID and config.ADMIN_TELEGRAM_ID != 0


def _log_unauthorized(message: Message) -> None:
    user = message.from_user
    logger.warning(
        "Unauthorized admin command attempt: telegram_id=%s username=%s command=%s",
        user.id, user.username or "-", message.text or "-",
    )


def _admin_message_allowed(message: Message) -> bool:
    if is_admin(message.from_user.id):
        return True
    _log_unauthorized(message)
    return False


def _admin_callback_allowed(callback: CallbackQuery) -> bool:
    if is_admin(callback.from_user.id):
        return True
    logger.warning(
        "Unauthorized admin callback attempt: telegram_id=%s username=%s callback=%s",
        callback.from_user.id, callback.from_user.username or "-", callback.data or "-",
    )
    return False


def _panel_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        ("👥 Пользователи", "users:0"), ("📁 Категории", "categories"),
        ("💰 Транзакции", "transactions"), ("🎯 Бюджеты", "budgets"),
        ("🤝 Долги", "debts"), ("💳 Кошельки", "wallets"),
        ("💱 Курсы валют", "rates"), ("⚙️ Статус сервисов", "services"),
        ("📜 Логи и ошибки", "logs"), ("🗄 База данных", "database"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=label, callback_data=f"admin2:{data}")
    ] for label, data in buttons])


def _back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="admin2:home")
    ]])


def _users_keyboard(page: int, total_pages: int, users: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=f"👤 {label}", callback_data=f"admin2:user:{user_id}")]
            for user_id, label in users]
    navigation = []
    if page > 0:
        navigation.append(InlineKeyboardButton(text="◀️ Пред", callback_data=f"admin2:users:{page - 1}"))
    if page + 1 < total_pages:
        navigation.append(InlineKeyboardButton(text="След ▶️", callback_data=f"admin2:users:{page + 1}"))
    if navigation:
        rows.append(navigation)
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="admin2:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _read_log_lines(limit: int) -> list[str]:
    if not LOG_FILE.exists():
        return ["Файл логов пока не создан."]
    with LOG_FILE.open("r", encoding="utf-8", errors="replace") as log_file:
        return [_sanitize_log_line(line.rstrip()) for line in log_file.readlines()[-limit:]]


def _sanitize_log_line(line: str) -> str:
    for secret in (config.POSTGRES_PASSWORD, config.TELEGRAM_BOT_TOKEN):
        if secret:
            line = line.replace(secret, "[REDACTED]")
    return re.sub(r"(?i)(password|token|api[_-]?key)=\S+", r"\1=[REDACTED]", line)


def _message(text_to_send: str) -> str:
    if len(text_to_send) <= MAX_MESSAGE_LENGTH:
        return text_to_send
    return text_to_send[:MAX_MESSAGE_LENGTH] + "\n<i>Вывод сокращён.</i>"


def _fmt(value) -> str:
    return f"{float(value or 0):,.2f}"


def _account_link(user: User) -> str:
    name = html.escape(user.username or str(user.telegram_id))
    return f'<a href="tg://user?id={user.telegram_id}">{name}</a>'


@router.message(F.text == "🛠 Админ-панель")
async def open_admin_panel(message: Message):
    if not _admin_message_allowed(message):
        return
    await message.answer(
        "<b>🛠 Админ-панель</b>\nВыберите раздел:",
        reply_markup=_panel_keyboard(),
        parse_mode="HTML",
    )
    await message.answer(
        "Главное меню администратора обновлено.",
        reply_markup=get_main_menu_reply_keyboard(lang="ru", is_admin=True),
    )


@router.message(Command("admin"))
async def legacy_admin_command(message: Message):
    if not _admin_message_allowed(message):
        return
    await message.answer(
        "<b>🛠 Админ-панель</b>\nВыберите раздел:",
        reply_markup=_panel_keyboard(),
        parse_mode="HTML",
    )
    await message.answer(
        "Главное меню администратора обновлено.",
        reply_markup=get_main_menu_reply_keyboard(lang="ru", is_admin=True),
    )


@router.message(Command("admin_users"))
async def legacy_admin_users(message: Message):
    if not _admin_message_allowed(message):
        return
    body, keyboard = await _users_page(0)
    await message.answer(_message(body), reply_markup=keyboard, parse_mode="HTML")


@router.message(Command("admin_errors"))
async def legacy_admin_errors(message: Message):
    if not _admin_message_allowed(message):
        return
    await message.answer(_message(await _logs_text()), reply_markup=_back_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("admin2:"))
async def admin_callback(callback: CallbackQuery):
    if not _admin_callback_allowed(callback):
        return
    payload = callback.data.removeprefix("admin2:")
    if payload == "home":
        body, keyboard = await _home_text(), _panel_keyboard()
    elif payload.startswith("users:"):
        body, keyboard = await _users_page(max(0, int(payload.split(":", 1)[1])))
    elif payload.startswith("user:"):
        body, keyboard = await _user_detail(int(payload.split(":", 1)[1]))
    else:
        builders = {
            "categories": _categories_text, "transactions": _transactions_text,
            "budgets": _budgets_text, "debts": _debts_text, "wallets": _wallets_text,
            "rates": _rates_text, "services": _services_text, "logs": _logs_text,
            "database": _database_text,
        }
        body = await builders.get(payload, _home_text)()
        keyboard = _back_keyboard()
    await callback.answer()
    await callback.message.edit_text(_message(body), reply_markup=keyboard, parse_mode="HTML")


async def _home_text() -> str:
    return "<b>🛠 Админ-панель</b>\nВыберите раздел:"


async def _users_page(page: int):
    async with AsyncSessionLocal() as session:
        total = int(await session.scalar(select(func.count()).select_from(User)) or 0)
        total_pages = max(1, (total + USERS_PER_PAGE - 1) // USERS_PER_PAGE)
        page = min(page, total_pages - 1)
        result = await session.execute(
            select(User, func.count(Transaction.id).label("tx_count"))
            .outerjoin(Transaction, Transaction.user_id == User.id)
            .group_by(User.id).order_by(User.created_at.desc())
            .offset(page * USERS_PER_PAGE).limit(USERS_PER_PAGE)
        )
        rows = result.all()
    lines = [f"<b>👥 Пользователи</b>  <code>{page + 1}/{total_pages}</code>", ""]
    for user, tx_count in rows:
        registered = user.created_at.strftime("%Y-%m-%d") if user.created_at else "-"
        lines.append(f"{_account_link(user)} · {registered} · {user.language} · {user.base_currency} · операций: <b>{tx_count}</b>")
    if not rows:
        lines.append("Пользователей пока нет.")
    labels = [(user.id, user.username or str(user.telegram_id)) for user, _ in rows]
    return "\n".join(lines), _users_keyboard(page, total_pages, labels)


async def _user_detail(user_id: int):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            return "Пользователь не найден.", _back_keyboard()
        stats = (await session.execute(select(
            func.count(Transaction.id),
            func.coalesce(func.sum(case((Transaction.type == "expense", Transaction.amount_base), else_=0)), 0),
            func.coalesce(func.sum(case((Transaction.type == "income", Transaction.amount_base), else_=0)), 0),
            func.max(Transaction.occurred_at),
        ).where(Transaction.user_id == user_id))).one()
        top = (await session.execute(
            select(Category.name, func.count(Transaction.id)).join(Transaction, Transaction.category_id == Category.id)
            .where(Transaction.user_id == user_id, Transaction.type == "expense")
            .group_by(Category.id, Category.name).order_by(func.count(Transaction.id).desc()).limit(3)
        )).all()
        budgets = (await session.execute(select(Budget.monthly_limit, Budget.currency).where(Budget.user_id == user_id))).all()
        recurring = (await session.execute(select(RecurringPayment.amount, RecurringPayment.currency, RecurringPayment.comment).where(RecurringPayment.user_id == user_id, RecurringPayment.is_active == True))).all()
    count, expense, income, last_activity = stats
    top_text = "\n".join(f"• {html.escape(name)} — {count}" for name, count in top) or "нет данных"
    budget_text = "\n".join(f"• {amount} {currency}" for amount, currency in budgets) or "нет данных (кошельки не заведены в схеме)"
    recurring_text = "\n".join(f"• {amount} {currency} — {html.escape(comment or 'без комментария')}" for amount, currency, comment in recurring) or "нет активных регулярных платежей"
    body = (
        f"<b>👤 Карточка пользователя</b>\n\nАккаунт: {_account_link(user)}\n"
        f"Telegram ID: <code>{user.telegram_id}</code>\nРегистрация: {user.created_at:%Y-%m-%d %H:%M}\n"
        f"Язык: {user.language}\nБазовая валюта: {user.base_currency}\n\n"
        f"<b>💰 Финансы</b>\nОпераций: <b>{count}</b>\nРасходы: <b>{_fmt(expense)} {user.base_currency}</b>\n"
        f"Доходы: <b>{_fmt(income)} {user.base_currency}</b>\nПоследняя активность: {last_activity or 'нет данных'}\n\n"
        f"<b>📁 Топ-3 категории трат</b>\n{top_text}\n\n<b>💳 Кошельки</b>\n{budget_text}\n\n"
        "<b>🤝 Открытые долги</b>\nнет данных (таблица долгов не заведена в схеме)\n\n"
        f"<b>🔁 Активные регулярные платежи</b>\n{recurring_text}"
    )
    return body, _back_keyboard()


async def _categories_text() -> str:
    async with AsyncSessionLocal() as session:
        categories = (await session.execute(select(Category.name, Category.is_default, User.username).outerjoin(User, Category.user_id == User.id).order_by(Category.is_default.desc(), Category.name))).all()
        top = (await session.execute(select(Category.name, func.count(Transaction.id)).join(Transaction, Transaction.category_id == Category.id).group_by(Category.id, Category.name).order_by(func.count(Transaction.id).desc()).limit(10))).all()
    lines = ["<b>📁 Категории</b>", "", "<b>Все категории</b>"]
    lines.extend(f"• {html.escape(name)} — {'дефолтная' if is_default else 'добавил @' + (username or '-')}" for name, is_default, username in categories)
    lines.extend(["", "<b>Топ-10 по операциям</b>"])
    lines.extend(f"• {html.escape(name)} — <b>{count}</b>" for name, count in top)
    return "\n".join(lines)


async def _transactions_text() -> str:
    now = datetime.now(timezone.utc)
    periods = [("Всего", None), ("Сегодня", now.replace(hour=0, minute=0, second=0, microsecond=0)), ("7 дней", now - timedelta(days=7)), ("Месяц", now - timedelta(days=30))]
    async with AsyncSessionLocal() as session:
        period_lines = []
        for label, since in periods:
            condition = [] if since is None else [Transaction.occurred_at >= since]
            count, total = (await session.execute(select(func.count(Transaction.id), func.coalesce(func.sum(Transaction.amount_base), 0)).where(*condition))).one()
            period_lines.append(f"• {label}: <b>{count}</b> операций, <b>{_fmt(total)}</b> TJS")
        currencies = (await session.execute(select(Transaction.currency, func.count(Transaction.id)).group_by(Transaction.currency).order_by(Transaction.currency))).all()
    return "<b>💰 Транзакции</b>\n\n" + "\n".join(period_lines) + "\n\n<b>По валютам</b>\n" + "\n".join(f"• {currency}: <b>{count}</b>" for currency, count in currencies)


async def _budgets_text() -> str:
    async with AsyncSessionLocal() as session:
        count = await session.scalar(select(func.count()).select_from(Budget)) or 0
        total = await session.scalar(select(func.coalesce(func.sum(Budget.monthly_limit), 0)))
    return f"<b>🎯 Бюджеты</b>\n\nЗаписей: <b>{count}</b>\nСумма лимитов: <b>{_fmt(total)}</b>"


async def _debts_text() -> str:
    return "<b>🤝 Долги</b>\n\nТаблица долгов пока отсутствует в текущей схеме БД."


async def _wallets_text() -> str:
    return "<b>💳 Кошельки</b>\n\nОтдельная таблица кошельков пока отсутствует в текущей схеме БД."


async def _rates_text() -> str:
    async with AsyncSessionLocal() as session:
        rates = (await session.execute(select(ExchangeRate).order_by(ExchangeRate.fetched_at.desc()).limit(20))).scalars().all()
    if not rates:
        return "<b>💱 Курсы валют</b>\n\nДанных пока нет."
    latest = rates[0]
    lines = [f"<b>💱 Курсы валют</b>\nОбновлено: {latest.fetched_at:%Y-%m-%d %H:%M UTC}", ""]
    lines.extend(f"• {rate.currency}/{rate.base_currency}: <code>{rate.rate}</code>" for rate in rates)
    return "\n".join(lines)


async def _services_text() -> str:
    jobs = scheduler.get_jobs()
    lines = [f"<b>⚙️ Статус сервисов</b>\nAPScheduler: <b>{'работает' if scheduler.running else 'остановлен'}</b>", ""]
    for job in jobs:
        next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S %Z") if job.next_run_time else "не запланирован"
        lines.append(f"• {html.escape(job.id)} — {next_run}")
    return "\n".join(lines)


async def _logs_text() -> str:
    now = datetime.now(timezone.utc)
    recent_errors = []
    for line in _read_log_lines(500):
        if not any(marker in line for marker in (" ERROR ", " EXCEPTION ", "Traceback", "Exception")):
            continue
        try:
            timestamp = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
            if timestamp >= (now - timedelta(hours=24)).replace(tzinfo=None):
                recent_errors.append(line)
        except ValueError:
            continue
    errors = "\n".join(recent_errors[-15:]) or "Ошибок за последние 24 часа нет."
    return "<b>📜 Логи и ошибки</b>\n\n<b>Последние 15 строк</b>\n<pre>" + html.escape("\n".join(_read_log_lines(15))) + "</pre>\n\n<b>ERROR/EXCEPTION за 24 часа</b>\n<pre>" + html.escape(errors) + "</pre>"


async def _database_text() -> str:
    async with AsyncSessionLocal() as session:
        size_mb = await session.scalar(text("SELECT pg_database_size(current_database()) / 1024.0 / 1024.0"))
        counts = []
        for table_name in Base.metadata.tables:
            count = await session.scalar(text(f'SELECT COUNT(*) FROM "{table_name}"'))
            counts.append(f"• {table_name}: <b>{count}</b>")
    return f"<b>🗄 База данных</b>\nРазмер: <b>{float(size_mb or 0):.2f} MB</b>\n\n" + "\n".join(counts)