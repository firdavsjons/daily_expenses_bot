from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List
from bot.models import Category
from bot.i18n import get_text
from bot.i18n.categories import get_category_name

def get_language_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"),
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_lang_uz"),
        ],
        [
            InlineKeyboardButton(text="🇹🇯 Тоҷикӣ", callback_data="set_lang_tj"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_currency_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🇹🇯 TJS", callback_data="set_currency_TJS"),
            InlineKeyboardButton(text="🇷🇺 RUB", callback_data="set_currency_RUB"),
            InlineKeyboardButton(text="🇺🇸 USD", callback_data="set_currency_USD"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_category_selection_keyboard(categories: List[Category], pending_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Inline keyboard for choosing category when NLP parser needs user confirmation.
    """
    buttons = []
    row = []
    for cat in categories:
        icon = cat.icon or "📁"
        localized_name = get_category_name(cat.name, lang)
        row.append(InlineKeyboardButton(
            text=f"{icon} {localized_name}",
            callback_data=f"select_cat:{pending_id}:{cat.id}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_undo_keyboard(transaction_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=get_text("btn_undo", lang),
            callback_data=f"undo:{transaction_id}"
        )
    ]])

def get_undo_confirmation_keyboard(transaction_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=get_text("btn_undo_confirm", lang),
            callback_data=f"undo_confirm:{transaction_id}"
        ),
        InlineKeyboardButton(
            text=get_text("btn_undo_cancel", lang),
            callback_data=f"undo_cancel:{transaction_id}"
        )
    ]])

def get_main_menu_reply_keyboard(lang: str = "ru", is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text=get_text("btn_today", lang)),
            KeyboardButton(text=get_text("btn_month", lang))
        ],
        [
            KeyboardButton(text=get_text("btn_rates", lang)),
            KeyboardButton(text=get_text("btn_categories", lang))
        ],
        [
            KeyboardButton(text=get_text("btn_currency", lang)),
            KeyboardButton(text=get_text("btn_recurring", lang))
        ],
        [
            KeyboardButton(text=get_text("btn_language", lang))
        ]
    ]
    if is_admin:
        keyboard[-1].append(KeyboardButton(text="🛠 Админ-панель"))
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
