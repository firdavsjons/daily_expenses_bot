import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.models import Category

logger = logging.getLogger(__name__)

DEFAULT_CATEGORIES = [
    # Expenses
    {
        "name": "Еда",
        "type": "expense",
        "icon": "🍎",
        "is_default": True,
        "keywords": ["еда", "яблоко", "хлеб", "молоко", "кафе", "обед", "ужин", "продукты", "магазин", "фрукты", "питание", "ресторан", "перекус", "супермаркет", "пицца", "суши", "бургер", "olma", "себ", "apple", "ovqat", "гизо", "ош", "нон", "non", "food", "lunch", "dinner", "breakfast", "нонушта", "choy", "палов", "пилав"]
    },
    {
        "name": "Транспорт",
        "type": "expense",
        "icon": "🚕",
        "is_default": True,
        "keywords": ["транспорт", "такси", "автобус", "метро", "бензин", "проезд", "маршрутка", "заправка", "парковка", "топливо", "дорога", "taksi", "taxi", "avtobus", "bus", "benzin", "gas", "fuel"]
    },
    {
        "name": "Жильё и коммуналка",
        "type": "expense",
        "icon": "🏠",
        "is_default": True,
        "keywords": ["жилье", "коммуналка", "аренда", "квартира", "свет", "вода", "газ", "электричество", "отопление", "квартплата", "дом", "коммунальные", "ijara", "rent", "уй", "хона", "сув", "water"]
    },
    {
        "name": "Здоровье",
        "type": "expense",
        "icon": "💊",
        "is_default": True,
        "keywords": ["здоровье", "аптека", "лекарства", "врач", "больница", "анализы", "доктор", "стоматолог", "медицина", "таблетки", "клиника", "dori", "дорихона", "pharmacy", "medicine", "doctor", "шифохона"]
    },
    {
        "name": "Развлечения",
        "type": "expense",
        "icon": "🎉",
        "is_default": True,
        "keywords": ["развлечения", "кино", "билеты", "концерт", "игра", "игры", "отдых", "парк", "боулинг", "театр", "тусовка", "клуб", "kino", "cinema", "movie", "game", "party"]
    },
    {
        "name": "Одежда",
        "type": "expense",
        "icon": "👕",
        "is_default": True,
        "keywords": ["одежда", "обувь", "куртка", "штаны", "футболка", "кроссовки", "платье", "вещи", "джинсы", "рубашка", "носки", "kiyim", "clothes", "shoes", "poyabzal"]
    },
    {
        "name": "Связь и интернет",
        "type": "expense",
        "icon": "📱",
        "is_default": True,
        "keywords": ["связь", "интернет", "телефон", "мобильный", "симка", "вайфай", "wifi", "мегафон", "тселл", "tcell", "babilon", "zain", "билайн", "баланс", "phone", "mobile", "internet"]
    },
    {
        "name": "Образование",
        "type": "expense",
        "icon": "📚",
        "is_default": True,
        "keywords": ["образование", "курсы", "учеба", "книги", "учебник", "университет", "школа", "обучение", "тренинг", "лекция", "урок", "kitob", "китоб", "book", "school", "course", "maktab"]
    },
    {
        "name": "Подарки",
        "type": "expense",
        "icon": "🎁",
        "is_default": True,
        "keywords": ["подарки", "подарок", "презент", "цветы", "сувенир", "день рождения", "др", "sovg'a", "туҳфа", "gift", "present", "flowers", "gullar"]
    },
    {
        "name": "Питомцы",
        "type": "expense",
        "icon": "🐾",
        "is_default": True,
        "keywords": ["питомцы", "кот", "собака", "корма", "корм", "ветеринар", "животные", "щенок", "кошечка", "пёс", "mushuk", "cat", "dog", "pet", "pets"]
    },
    {
        "name": "Разное",
        "type": "expense",
        "icon": "🔧",
        "is_default": True,
        "keywords": ["разное", "прочее", "мелочь", "прочие расходы", "другое", "покупка", "boshqa", "other"]
    },

    # Income
    {
        "name": "Зарплата",
        "type": "income",
        "icon": "💼",
        "is_default": True,
        "keywords": ["зарплата", "зп", "получил", "аванс", "оклад", "получение", "заработал", "премия", "получила", "заработок", "maosh", "oylik", "маош", "salary", "wage"]
    },
    {
        "name": "Подарок",
        "type": "income",
        "icon": "🎁",
        "is_default": True,
        "keywords": ["подарок", "подарили", "денежный подарок", "sovg'a", "туҳфа", "gift"]
    },
    {
        "name": "Прочий доход",
        "type": "income",
        "icon": "💰",
        "is_default": True,
        "keywords": ["доход", "прочий доход", "подработка", "фриланс", "кэшбэк", "проценты", "продажа", "поступление", "daromad", "даромад", "income", "profit"]
    }
]

async def seed_default_categories(session: AsyncSession):
    """
    Seeds missing default categories and updates keywords for multi-language support.
    """
    result = await session.execute(
        select(Category).where(Category.is_default == True, Category.user_id.is_(None))
    )
    existing_defaults = {cat.name: cat for cat in result.scalars().all()}

    changed_count = 0
    for cat_data in DEFAULT_CATEGORIES:
        name = cat_data["name"]
        if name not in existing_defaults:
            category = Category(
                name=name,
                type=cat_data["type"],
                icon=cat_data["icon"],
                is_default=True,
                user_id=None,
                keywords=cat_data["keywords"]
            )
            session.add(category)
            changed_count += 1
        else:
            # Update keywords if expanded
            cat_obj = existing_defaults[name]
            updated_keywords = list(set((cat_obj.keywords or []) + cat_data["keywords"]))
            if len(updated_keywords) != len(cat_obj.keywords or []):
                cat_obj.keywords = updated_keywords
                changed_count += 1

    if changed_count > 0:
        await session.commit()
        logger.info(f"Updated/Seeded default categories ({changed_count} updated).")
    else:
        logger.info("Default categories up to date.")
