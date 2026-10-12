import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from rapidfuzz.fuzz import partial_ratio

FUZZY_MATCH_THRESHOLD = 85

@dataclass
class ParsedTransaction:
    amount: float
    currency: str
    type: str  # 'expense' or 'income'
    category_id: Optional[int]
    category_name: Optional[str]
    comment: str
    raw_text: str

CURRENCY_PATTERNS = {
    "TJS": [r"\bсомони\b", r"\bсмн\b", r"\bсм\b", r"\bсом\b", r"\btjs\b", r"\bsomoni\b", r"\bsomon\b"],
    "RUB": [r"\bрублей\b", r"\bрубль\b", r"\bрубля\b", r"\bруб\b", r"\bр\.\b", r"\bр\b", r"\brub\b", r"\brubl\b", r"\brouble\b"],
    "USD": [r"\bдолларов\b", r"\bдоллар\b", r"\bдоллара\b", r"\bдолл\b", r"\busd\b", r"\bбакс\b", r"\bбаксов\b", r"\bdollar\b", r"\bdollars\b", r"\$"]
}

LEARNING_STOP_WORDS = {
    "за", "на", "из", "в", "во", "и", "я", "мы", "купил", "купила", "потратил",
    "потратила", "оплатил", "оплатила", "получил", "получила", "для", "это", "мне",
    "сом", "сомони", "см", "смн", "руб", "рубль", "рубля", "рублей", "доллар", "доллара",
    "долларов", "долл", "бакс", "баксов", "tjs", "rub", "usd",
}


def extract_learning_keywords(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower())
    return [word for word in words if len(word) >= 3 and word not in LEARNING_STOP_WORDS]

INCOME_KEYWORDS = [
    "зарплата", "зп", "получил", "получила", "доход", "заработал", "заработала",
    "аванс", "премия", "подарили", "подарок", "фриланс", "кэшбэк", "поступление",
    "maosh", "oylik", "daromad", "sovg'a", "маош", "даромад", "туҳфа", "salary", "income", "wage", "bonus", "gift", "earnings"
]

def parse_transaction_message(
    text: str,
    categories: List[Dict[str, Any]],
    base_currency: str = "TJS",
    learned_keywords: Optional[List[Dict[str, Any]]] = None,
) -> Optional[ParsedTransaction]:
    """
    Parses free-text message into structured ParsedTransaction object.
    
    :param text: User message text.
    :param categories: List of dicts with keys: 'id', 'name', 'type', 'keywords', 'icon'
    :param base_currency: User's fallback currency.
    :return: ParsedTransaction or None if amount is missing.
    """
    cleaned_text = text.strip()
    if not cleaned_text:
        return None

    lower_text = cleaned_text.lower()

    # 1. Extract Amount
    # Supports formats: $10, 10$, 10.50, 10,50, 10
    amount_match = re.search(r'\$?(\d+(?:[.,]\d+)?)\$?', lower_text)
    if not amount_match:
        return None

    raw_amount_str = amount_match.group(1).replace(',', '.')
    try:
        amount = float(raw_amount_str)
    except ValueError:
        return None

    if amount <= 0:
        return None

    # Amount token location for removal from comment
    amount_full_match = amount_match.group(0)

    # 2. Extract Currency
    found_currency = None

    # Check for '$' symbol in raw text first
    if '$' in lower_text:
        found_currency = "USD"
    else:
        for curr, patterns in CURRENCY_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, lower_text):
                    found_currency = curr
                    break
            if found_currency:
                break

    if not found_currency:
        found_currency = base_currency

    # 3. Extract Type (Expense vs Income)
    is_income = any(re.search(r'\b' + re.escape(kw) + r'\b', lower_text) for kw in INCOME_KEYWORDS)
    tx_type = "income" if is_income else "expense"

    # 4. Extract Category by matching keywords
    matched_category_id = None
    matched_category_name = None
    max_score = 0

    # Tokenize text into words
    words = re.findall(r'[a-zA-Zа-яА-ЯёЁ0-9]+', lower_text)

    # Personal vocabulary has priority over global category keywords.
    for learned in learned_keywords or []:
        keyword = str(learned.get("keyword", "")).lower()
        if keyword and keyword in words:
            matched_category_id = learned.get("category_id")
            matched_category_name = learned.get("category_name")
            break

    for cat in categories if not matched_category_name else []:
        # Match type if category has specific type
        cat_type = cat.get("type", "expense")
        cat_keywords = cat.get("keywords", [])
        cat_name = cat.get("name", "")

        # Score calculation: check if any keyword is contained in words or vice versa
        score = 0
        for kw in cat_keywords:
            kw_lower = kw.lower()
            if kw_lower in lower_text:
                score += len(kw_lower) * 2
                if any(w == kw_lower for w in words):
                    score += 10
                continue

            # Compare individual message words only after exact matching fails.
            # Short keywords are intentionally excluded to avoid false positives.
            if len(kw_lower) >= 3:
                best_fuzzy_score = max(
                    (partial_ratio(word, kw_lower) for word in words if len(word) >= 3),
                    default=0,
                )
                if best_fuzzy_score >= FUZZY_MATCH_THRESHOLD:
                    score += len(kw_lower) * 2 * (best_fuzzy_score / 100)

        if score > max_score:
            max_score = score
            matched_category_id = cat.get("id")
            matched_category_name = cat_name
            # If explicit category has type income/expense, adjust tx_type if appropriate
            if cat_type == "income" and not is_income:
                tx_type = "income"

    if not matched_category_name:
        # Fallback category
        matched_category_name = "Разное"

    # 5. Extract Comment (clean out amount and currency tokens)
    comment_text = lower_text
    comment_text = comment_text.replace(amount_full_match, "", 1)

    # Remove currency words
    for curr_patterns in CURRENCY_PATTERNS.values():
        for pat in curr_patterns:
            comment_text = re.sub(pat, "", comment_text)

    # Clean punctuation and extra spaces
    comment_text = re.sub(r'[\$\s\.,\-\:=]+', ' ', comment_text).strip()

    # Capitalize first letter of comment
    final_comment = comment_text.capitalize() if comment_text else matched_category_name

    return ParsedTransaction(
        amount=amount,
        currency=found_currency,
        type=tx_type,
        category_id=matched_category_id,
        category_name=matched_category_name,
        comment=final_comment,
        raw_text=cleaned_text
    )
