import io
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional, List, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.models import Transaction, Category, User, utc_now
from bot.i18n import get_text
from bot.i18n.categories import get_category_name

def get_period_dates(period_name: str) -> Tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    if period_name == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period_name == "week":
        start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period_name == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:
        start = now - timedelta(days=30)
        end = now
    return start, end

async def generate_period_report(
    session: AsyncSession,
    user: User,
    start_date: datetime,
    end_date: datetime
) -> Tuple[str, Optional[bytes]]:
    """
    Generates text summary and optional Matplotlib Pie Chart photo bytes for the period.
    """
    lang = user.language if user.language else "ru"

    # Fetch transactions in date range
    stmt = (
        select(Transaction)
        .options(selectinload(Transaction.category))
        .where(
            Transaction.user_id == user.id,
            Transaction.occurred_at >= start_date,
            Transaction.occurred_at <= end_date
        )
        .order_by(Transaction.occurred_at.asc())
    )
    result = await session.execute(stmt)
    transactions = result.scalars().all()

    period_label = f"{start_date.strftime('%d.%m.%Y')} — {end_date.strftime('%d.%m.%Y')}"
    if not transactions:
        return get_text("report_no_data", lang=lang, period=period_label), None

    total_expense = 0.0
    total_income = 0.0
    category_expenses: Dict[str, float] = {}

    for tx in transactions:
        amount_base = float(tx.amount_base)
        cat_name = get_category_name(tx.category.name if tx.category else "Разное", lang)
        icon = tx.category.icon if (tx.category and tx.category.icon) else "📁"
        full_cat = f"{icon} {cat_name}"

        if tx.type == "expense":
            total_expense += amount_base
            category_expenses[full_cat] = category_expenses.get(full_cat, 0.0) + amount_base
        else:
            total_income += amount_base

    # Compare with previous period of equal length
    period_duration = end_date - start_date
    prev_start = start_date - period_duration
    prev_end = start_date

    prev_stmt = (
        select(func.sum(Transaction.amount_base))
        .where(
            Transaction.user_id == user.id,
            Transaction.type == "expense",
            Transaction.occurred_at >= prev_start,
            Transaction.occurred_at < prev_end
        )
    )
    prev_res = await session.execute(prev_stmt)
    prev_expense_sum = prev_res.scalar() or 0.0
    prev_expense = float(prev_expense_sum)

    diff_str = ""
    if prev_expense > 0:
        pct_change = ((total_expense - prev_expense) / prev_expense) * 100
        sign = "+" if pct_change > 0 else ""
        diff_str = get_text(
            "report_prev_comparison",
            lang=lang,
            sign=sign,
            pct=pct_change,
            prev_amount=prev_expense,
            currency=user.base_currency
        )

    # Format text response
    text_lines = [
        get_text("report_header", lang=lang, period=period_label),
        get_text("report_base_curr", lang=lang, currency=user.base_currency),
        "",
        get_text("report_total_expense", lang=lang, amount=total_expense, currency=user.base_currency),
        get_text("report_total_income", lang=lang, amount=total_income, currency=user.base_currency),
        get_text("report_balance", lang=lang, amount=(total_income - total_expense), currency=user.base_currency),
        diff_str,
        "",
        get_text("report_by_categories", lang=lang)
    ]

    sorted_cats = sorted(category_expenses.items(), key=lambda x: x[1], reverse=True)
    for cat, sum_val in sorted_cats:
        pct = (sum_val / total_expense * 100) if total_expense > 0 else 0
        text_lines.append(f"• {cat}: `{sum_val:.2f} {user.base_currency}` ({pct:.1f}%)")

    text_msg = "\n".join([line for line in text_lines if line is not None])

    # Generate Pie Chart image if there are expenses
    chart_bytes = None
    if category_expenses and total_expense > 0:
        chart_bytes = generate_pie_chart(category_expenses, user.base_currency, lang=lang)

    return text_msg, chart_bytes

def generate_pie_chart(category_data: Dict[str, float], base_currency: str, lang: str = "ru") -> bytes:
    """
    Generates Matplotlib pie chart image bytes.
    """
    labels = list(category_data.keys())
    values = list(category_data.values())

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(aspect="equal"))

    colors = plt.cm.tab20.colors[:len(labels)]

    wedges, texts, autotexts = ax.pie(
        values,
        autopct='%1.1f%%',
        pctdistance=0.75,
        startangle=140,
        colors=colors,
        textprops=dict(color="w", weight="bold")
    )

    ax.legend(
        wedges,
        [f"{lbl} ({val:.1f} {base_currency})" for lbl, val in zip(labels, values)],
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )

    plt.setp(autotexts, size=9, weight="bold")
    title_text = get_text("report_chart_title", lang=lang, currency=base_currency)
    ax.set_title(title_text, fontsize=14, pad=20, weight="bold", color="white")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", transparent=False)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

async def export_transactions_to_excel(
    session: AsyncSession,
    user: User,
    start_date: datetime,
    end_date: datetime
) -> bytes:
    """
    Exports transactions to Excel (.xlsx) file bytes.
    """
    stmt = (
        select(Transaction)
        .options(selectinload(Transaction.category))
        .where(
            Transaction.user_id == user.id,
            Transaction.occurred_at >= start_date,
            Transaction.occurred_at <= end_date
        )
        .order_by(Transaction.occurred_at.asc())
    )
    result = await session.execute(stmt)
    transactions = result.scalars().all()

    lang = user.language if user.language else "ru"
    data = []
    for tx in transactions:
        data.append({
            "ID": tx.id,
            "Date": tx.occurred_at.strftime("%Y-%m-%d %H:%M:%S"),
            "Type": "Expense" if tx.type == "expense" else "Income",
            "Category": get_category_name(tx.category.name if tx.category else "Разное", lang),
            "Amount": float(tx.amount),
            "Currency": tx.currency,
            "Base Amount": float(tx.amount_base),
            "Base Currency": user.base_currency,
            "Exchange Rate": float(tx.exchange_rate),
            "Comment": tx.comment or "",
            "Raw Text": tx.raw_text or ""
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Transactions")
    output.seek(0)
    return output.getvalue()
