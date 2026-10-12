from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from bot.services.report_service import generate_period_report


class FakeReportSession:
    def __init__(self, transactions):
        self.transactions = transactions

    async def execute(self, statement):
        statement_text = str(statement)
        if "sum(transactions.amount_base)" in statement_text:
            previous_sum = sum(
                transaction.amount_base
                for transaction in self.transactions
                if transaction.type == "expense"
            )
            return SimpleNamespace(scalar=lambda: previous_sum)
        return SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: self.transactions))


@pytest.mark.asyncio
async def test_daily_report_sums_converted_amount_base():
    category = SimpleNamespace(name="Еда", icon="🍎")
    user = SimpleNamespace(id=1, language="ru", base_currency="TJS")
    transactions = [
        SimpleNamespace(amount=5, amount_base=46, type="expense", category=category),
        SimpleNamespace(amount=10, amount_base=10, type="expense", category=category),
    ]
    session = FakeReportSession(transactions)
    start = datetime(2026, 9, 8, tzinfo=timezone.utc)
    end = datetime(2026, 9, 8, 23, 59, 59, tzinfo=timezone.utc)

    report_text, _ = await generate_period_report(session, user, start, end)

    assert "56.0" in report_text or "56.00" in report_text
    assert "15.0" not in report_text and "15.00" not in report_text