import pytest
from bot.parser import parse_transaction_message, ParsedTransaction

SAMPLE_CATEGORIES = [
    {
        "id": 1,
        "name": "Еда",
        "type": "expense",
        "icon": "🍎",
        "keywords": ["еда", "яблоко", "хлеб", "молоко", "кафе", "обед", "ужин", "продукты", "магазин", "фрукты", "olma", "себ", "apple", "ovqat", "food"]
    },
    {
        "id": 2,
        "name": "Транспорт",
        "type": "expense",
        "icon": "🚕",
        "keywords": ["транспорт", "такси", "автобус", "метро", "бензин", "проезд", "маршрутка", "заправка", "taksi", "taxi", "bus"]
    },
    {
        "id": 3,
        "name": "Зарплата",
        "type": "income",
        "icon": "💼",
        "keywords": ["зарплата", "зп", "получил", "аванс", "оклад", "заработал", "премия", "maosh", "oylik", "маош", "salary", "wage"]
    },
    {
        "id": 4,
        "name": "Разное",
        "type": "expense",
        "icon": "🔧",
        "keywords": ["разное", "прочее", "другое", "other", "boshqa"]
    }
]

def test_parse_kúpil_yabloko_za_10_somoni():
    res = parse_transaction_message("купил яблоко за 10 сомони", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 10.0
    assert res.currency == "TJS"
    assert res.type == "expense"
    assert res.category_name == "Еда"

def test_parse_yabloko_10_sm():
    res = parse_transaction_message("яблоко 10 см", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 10.0
    assert res.currency == "TJS"
    assert res.type == "expense"
    assert res.category_name == "Еда"

def test_parse_taksi_25_rub():
    res = parse_transaction_message("такси 25 руб", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 25.0
    assert res.currency == "RUB"
    assert res.type == "expense"
    assert res.category_name == "Транспорт"

def test_parse_fuzzy_takso_typo():
    res = parse_transaction_message("таксо 25 руб", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.category_name == "Транспорт"

def test_parse_fuzzy_produkti_typo():
    res = parse_transaction_message("продукти 120 сомони", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.category_name == "Еда"

def test_parse_fuzzy_avtobus_typo():
    res = parse_transaction_message("автобусс 10 сом", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.category_name == "Транспорт"

def test_parse_personal_learned_keyword_before_global_keywords():
    learned = [{"keyword": "кофейня", "category_id": 9, "category_name": "Моя категория"}]
    res = parse_transaction_message("кофейня 40 сомони", SAMPLE_CATEGORIES, learned_keywords=learned)
    assert res is not None
    assert res.category_id == 9
    assert res.category_name == "Моя категория"

def test_parse_obed_15_dollar_symbol():
    res = parse_transaction_message("обед 15$", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 15.0
    assert res.currency == "USD"
    assert res.type == "expense"
    assert res.category_name == "Еда"

def test_parse_zarplata_500_dollar():
    res = parse_transaction_message("зарплата 500 доллар", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 500.0
    assert res.currency == "USD"
    assert res.type == "income"
    assert res.category_name == "Зарплата"

def test_parse_150_taksi():
    res = parse_transaction_message("150 такси", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 150.0
    assert res.currency == "TJS"
    assert res.type == "expense"
    assert res.category_name == "Транспорт"

def test_parse_potratil_200_na_produkty():
    res = parse_transaction_message("потратил 200 на продукты", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 200.0
    assert res.currency == "TJS"
    assert res.type == "expense"
    assert res.category_name == "Еда"

def test_parse_10_som():
    res = parse_transaction_message("10 сом", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 10.0
    assert res.currency == "TJS"
    assert res.type == "expense"

def test_parse_10_dollar_taksi():
    res = parse_transaction_message("$10 такси", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 10.0
    assert res.currency == "USD"
    assert res.type == "expense"
    assert res.category_name == "Транспорт"

def test_parse_poluchil_premiyu_10000_rub():
    res = parse_transaction_message("получил премию 10000 руб", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 10000.0
    assert res.currency == "RUB"
    assert res.type == "income"
    assert res.category_name == "Зарплата"

def test_parse_uzbek_olma_10_somoni():
    res = parse_transaction_message("olma 10 somoni", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 10.0
    assert res.currency == "TJS"
    assert res.category_name == "Еда"

def test_parse_tajik_seb_5_som():
    res = parse_transaction_message("себ 5 сом", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 5.0
    assert res.currency == "TJS"
    assert res.category_name == "Еда"

def test_parse_english_apple_15_dollar():
    res = parse_transaction_message("apple $15", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 15.0
    assert res.currency == "USD"
    assert res.category_name == "Еда"

def test_parse_english_salary_2000_dollars():
    res = parse_transaction_message("salary 2000 dollars", SAMPLE_CATEGORIES, "TJS")
    assert res is not None
    assert res.amount == 2000.0
    assert res.currency == "USD"
    assert res.type == "income"
    assert res.category_name == "Зарплата"

def test_parse_no_amount_returns_none():
    res = parse_transaction_message("просто привет как дела", SAMPLE_CATEGORIES, "TJS")
    assert res is None
