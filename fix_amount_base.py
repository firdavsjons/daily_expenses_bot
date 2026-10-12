"""One-time repair for historical transactions with an invalid amount_base."""

import asyncio
from datetime import timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.database import AsyncSessionLocal
from bot.models import ExchangeRate, Transaction, User


async def repair_amount_base() -> int:
    repaired = 0
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Transaction).options(selectinload(Transaction.user))
        )
        transactions = result.scalars().all()

        for transaction in transactions:
            user = transaction.user
            if not user:
                continue

            suspicious = (
                transaction.amount_base is None
                or float(transaction.amount_base) <= 0
                or (
                    transaction.currency != user.base_currency
                    and abs(float(transaction.amount_base) - float(transaction.amount)) < 0.01
                )
            )
            if not suspicious:
                continue

            rate = float(transaction.exchange_rate or 0)
            if rate <= 0 or (transaction.currency != user.base_currency and abs(rate - 1.0) < 0.000001):
                rate_query = (
                    select(ExchangeRate.rate)
                    .where(
                        ExchangeRate.currency == transaction.currency,
                        ExchangeRate.base_currency == user.base_currency,
                        ExchangeRate.fetched_at <= transaction.occurred_at,
                    )
                    .order_by(ExchangeRate.fetched_at.desc())
                    .limit(1)
                )
                rate = float(await session.scalar(rate_query) or 0)

                if rate <= 0 or (transaction.currency != user.base_currency and abs(rate - 1.0) < 0.000001):
                    reverse_query = (
                        select(ExchangeRate.rate)
                        .where(
                            ExchangeRate.currency == user.base_currency,
                            ExchangeRate.base_currency == transaction.currency,
                            ExchangeRate.fetched_at <= transaction.occurred_at,
                        )
                        .order_by(ExchangeRate.fetched_at.desc())
                        .limit(1)
                    )
                    reverse_rate = float(await session.scalar(reverse_query) or 0)
                    rate = 1.0 / reverse_rate if reverse_rate > 0 else 0

            if rate <= 0:
                latest_query = (
                    select(ExchangeRate.rate)
                    .where(
                        ExchangeRate.currency == transaction.currency,
                        ExchangeRate.base_currency == user.base_currency,
                    )
                    .order_by(ExchangeRate.fetched_at.desc())
                    .limit(1)
                )
                rate = float(await session.scalar(latest_query) or 0)

            if rate <= 0:
                if transaction.currency == user.base_currency:
                    rate = 1.0
                else:
                    print(f"Skipping transaction {transaction.id}: no exchange rate")
                    continue

            transaction.exchange_rate = rate
            transaction.amount_base = round(float(transaction.amount) * rate, 2)
            repaired += 1

        await session.commit()
    return repaired


if __name__ == "__main__":
    print(f"Repaired transactions: {asyncio.run(repair_amount_base())}")