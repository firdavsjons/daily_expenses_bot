import logging
import httpx
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from bot.models import ExchangeRate, utc_now

logger = logging.getLogger(__name__)

# Default fallback rates if API is unavailable
FALLBACK_RATES = {
    "TJS": 1.0,
    "USD": 10.65,  # 1 USD = ~10.65 TJS
    "RUB": 0.12,   # 1 RUB = ~0.12 TJS
}

async def fetch_and_update_rates(session: AsyncSession):
    """
    Fetches latest rates from open.er-api.com with base USD/TJS and saves to ExchangeRate table.
    """
    rates = {}
    
    # Primary API: open.er-api.com
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "https://open.er-api.com/v6/latest/USD"
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                all_rates = data.get("rates", {})
                tjs_rate = float(all_rates.get("TJS", 10.65))
                rub_rate = float(all_rates.get("RUB", 90.0))
                
                # 1 USD = tjs_rate TJS
                rates["USD"] = round(tjs_rate, 6)
                # 1 RUB = (tjs_rate / rub_rate) TJS
                if rub_rate > 0:
                    rates["RUB"] = round(tjs_rate / rub_rate, 6)
    except Exception as e:
        logger.warning(f"Failed to fetch rates from open.er-api: {e}")

    # Fallback to Frankfurter API if open.er-api failed
    if not rates:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = "https://api.frankfurter.app/latest?from=USD"
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    all_rates = data.get("rates", {})
                    tjs_rate = float(all_rates.get("TJS", 10.65))
                    rub_rate = float(all_rates.get("RUB", 90.0))
                    rates["USD"] = round(tjs_rate, 6)
                    if rub_rate > 0:
                        rates["RUB"] = round(tjs_rate / rub_rate, 6)
        except Exception as e:
            logger.warning(f"Failed to fetch rates from fallback API: {e}")

    # Use static defaults if both APIs failed
    if not rates:
        logger.warning("Using static fallback exchange rates.")
        rates = {"USD": FALLBACK_RATES["USD"], "RUB": FALLBACK_RATES["RUB"]}

    # Save to database
    now = utc_now()
    for curr, rate_val in rates.items():
        rate_entry = ExchangeRate(
            currency=curr,
            base_currency="TJS",
            rate=rate_val,
            fetched_at=now
        )
        session.add(rate_entry)

    await session.commit()
    logger.info(f"Updated exchange rates: {rates}")

async def get_latest_exchange_rate(session: AsyncSession, currency: str, base_currency: str = "TJS") -> float:
    """
    Returns rate to convert 'currency' into 'base_currency'.
    For instance: 100 USD -> amount_base = 100 * rate.
    """
    if currency == base_currency:
        return 1.0

    # Fetch latest stored rate for this currency against base_currency
    stmt = (
        select(ExchangeRate)
        .where(ExchangeRate.currency == currency, ExchangeRate.base_currency == base_currency)
        .order_by(desc(ExchangeRate.fetched_at))
        .limit(1)
    )
    result = await session.execute(stmt)
    latest_rate = result.scalar_one_or_none()

    if latest_rate:
        return float(latest_rate.rate)

    # Rates are normally stored against TJS. For the opposite direction,
    # use the reciprocal of the latest stored reverse rate.
    reverse_stmt = (
        select(ExchangeRate)
        .where(ExchangeRate.currency == base_currency, ExchangeRate.base_currency == currency)
        .order_by(desc(ExchangeRate.fetched_at))
        .limit(1)
    )
    reverse_result = await session.execute(reverse_stmt)
    reverse_rate = reverse_result.scalar_one_or_none()
    if reverse_rate and float(reverse_rate.rate) > 0:
        return 1.0 / float(reverse_rate.rate)

    # Fallback to defaults
    if currency == "USD":
        return FALLBACK_RATES["USD"]
    elif currency == "RUB":
        return FALLBACK_RATES["RUB"]
    elif currency == "TJS":
        return 1.0
    return 1.0
