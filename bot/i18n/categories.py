CATEGORY_TRANSLATIONS = {
    "Еда": {
        "ru": "Еда",
        "uz": "Oziq-ovqat",
        "tj": "Хӯрокворӣ",
        "en": "Food & Groceries"
    },
    "Транспорт": {
        "ru": "Транспорт",
        "uz": "Transport",
        "tj": "Нақлиёт",
        "en": "Transport"
    },
    "Жильё и коммуналка": {
        "ru": "Жильё и коммуналка",
        "uz": "Uy va kommunal",
        "tj": "Манзил ва коммуналӣ",
        "en": "Housing & Utilities"
    },
    "Здоровье": {
        "ru": "Здоровье",
        "uz": "Salomatlik",
        "tj": "Саломатӣ",
        "en": "Health & Pharmacy"
    },
    "Развлечения": {
        "ru": "Развлечения",
        "uz": "Hordiq chiqarish",
        "tj": "Дилхушӣ",
        "en": "Entertainment"
    },
    "Одежда": {
        "ru": "Одежда",
        "uz": "Kiyim-kechak",
        "tj": "Лобос",
        "en": "Clothes & Shoes"
    },
    "Связь и интернет": {
        "ru": "Связь и интернет",
        "uz": "Aloqa va internet",
        "tj": "Алоқа ва интернет",
        "en": "Telecom & Internet"
    },
    "Образование": {
        "ru": "Образование",
        "uz": "Ta'lim",
        "tj": "Таҳсилот",
        "en": "Education"
    },
    "Подарки": {
        "ru": "Подарки",
        "uz": "Sovg'alar",
        "tj": "Тӯҳфаҳо",
        "en": "Gifts"
    },
    "Питомцы": {
        "ru": "Питомцы",
        "uz": "Uy hayvonlari",
        "tj": "Ҳайвоноти хонагӣ",
        "en": "Pets"
    },
    "Разное": {
        "ru": "Разное",
        "uz": "Boshqalar",
        "tj": "Дигар",
        "en": "Other"
    },
    "Зарплата": {
        "ru": "Зарплата",
        "uz": "Maosh / Oylik",
        "tj": "Маош",
        "en": "Salary"
    },
    "Подарок": {
        "ru": "Подарок",
        "uz": "Sovg'a",
        "tj": "Тӯҳфа",
        "en": "Gift Income"
    },
    "Прочий доход": {
        "ru": "Прочий доход",
        "uz": "Boshqa daromad",
        "tj": "Даромади дигар",
        "en": "Other Income"
    }
}

def get_category_name(cat_name: str, lang: str = "ru") -> str:
    """
    Returns localized category name for display.
    If custom category or not found in dict, returns original cat_name.
    """
    lang_code = lang.lower() if lang else "ru"
    if cat_name in CATEGORY_TRANSLATIONS:
        return CATEGORY_TRANSLATIONS[cat_name].get(lang_code, cat_name)
    return cat_name
