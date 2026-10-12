from bot.i18n.ru import TRANSLATIONS as RU_DICT
from bot.i18n.uz import TRANSLATIONS as UZ_DICT
from bot.i18n.tj import TRANSLATIONS as TJ_DICT
from bot.i18n.en import TRANSLATIONS as EN_DICT

DICTIONARIES = {
    "ru": RU_DICT,
    "uz": UZ_DICT,
    "tj": TJ_DICT,
    "en": EN_DICT
}

def get_text(key: str, lang: str = "ru", **kwargs) -> str:
    """
    Returns localized text for specified key and language, falling back to 'ru' if missing.
    """
    lang_code = lang.lower() if lang else "ru"
    selected_dict = DICTIONARIES.get(lang_code, RU_DICT)

    template = selected_dict.get(key)
    if template is None:
        template = RU_DICT.get(key, key)

    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template

    return template
