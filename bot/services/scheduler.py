import logging
from datetime import datetime, timedelta, timezone
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, func
from bot.database import AsyncSessionLocal
from bot.models import User, Transaction, RecurringPayment, utc_now
from bot.services.currency_service import fetch_and_update_rates, get_latest_exchange_rate
from bot.keyboards import get_undo_keyboard

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Dushanbe")

async def job_update_exchange_rates():
    """Job to update exchange rates daily."""
    logger.info("Executing scheduled exchange rates update job...")
    async with AsyncSessionLocal() as session:
        try:
            await fetch_and_update_rates(session)
        except Exception as e:
            logger.error(f"Error in job_update_exchange_rates: {e}")

async def job_process_recurring_payments(bot: Bot):
    """Job to process scheduled recurring payments every 10 minutes."""
    now = utc_now()
    async with AsyncSessionLocal() as session:
        try:
            stmt = (
                select(RecurringPayment)
                .where(RecurringPayment.is_active == True, RecurringPayment.next_run_at <= now)
            )
            result = await session.execute(stmt)
            payments = result.scalars().all()

            for payment in payments:
                # Fetch user
                user_stmt = select(User).where(User.id == payment.user_id)
                user_res = await session.execute(user_stmt)
                user = user_res.scalar_one_or_none()
                if not user:
                    continue

                # Calculate rate
                rate = await get_latest_exchange_rate(session, payment.currency, user.base_currency)
                amount_base = float(payment.amount) * rate

                # Create transaction
                tx = Transaction(
                    user_id=payment.user_id,
                    category_id=payment.category_id,
                    amount=payment.amount,
                    currency=payment.currency,
                    amount_base=amount_base,
                    exchange_rate=rate,
                    raw_text=f"Регулярный платёж: {payment.comment or ''}",
                    comment=payment.comment or "Регулярный платёж",
                    type="expense",
                    occurred_at=now,
                    created_at=now
                )
                session.add(tx)

                # Update next_run_at
                if payment.frequency == "daily":
                    payment.next_run_at += timedelta(days=1)
                elif payment.frequency == "weekly":
                    payment.next_run_at += timedelta(weeks=1)
                elif payment.frequency == "monthly":
                    payment.next_run_at += timedelta(days=30)

                await session.commit()

                # Send notification to user
                try:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=f"🔄 *Исполнен регулярный платёж!*\n\n"
                            f"💰 Сумма: `{payment.amount} {payment.currency}`\n"
                            f"📝 Комментарий: {payment.comment or 'Регулярный с автооплатой'}",
                        reply_markup=get_undo_keyboard(tx.id, user.language or "ru")
                    )
                except Exception as send_err:
                    logger.warning(f"Could not send notification to user {user.telegram_id}: {send_err}")

        except Exception as e:
            logger.error(f"Error processing recurring payments: {e}")

async def job_daily_evening_reminder(bot: Bot):
    """Job to remind users at 21:00 if no transactions were added today."""
    now = utc_now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with AsyncSessionLocal() as session:
        try:
            users_stmt = select(User)
            users_res = await session.execute(users_stmt)
            users = users_res.scalars().all()

            for user in users:
                # Check transactions today
                tx_stmt = (
                    select(func.count(Transaction.id))
                    .where(Transaction.user_id == user.id, Transaction.occurred_at >= start_of_day)
                )
                tx_res = await session.execute(tx_stmt)
                count = tx_res.scalar() or 0

                if count == 0:
                    try:
                        await bot.send_message(
                            chat_id=user.telegram_id,
                            text="🔔 *Вечернее напоминание*\n\nВы ещё не внесли расходы за сегодня. Не забудьте записать свои траты! 📝"
                        )
                    except Exception as err:
                        logger.warning(f"Failed to send reminder to telegram_id {user.telegram_id}: {err}")

        except Exception as e:
            logger.error(f"Error running daily reminder job: {e}")

def setup_scheduler(bot: Bot):
    """Configures scheduler jobs and starts the scheduler."""
    # Daily exchange rates update at 00:05
    scheduler.add_job(job_update_exchange_rates, "cron", hour=0, minute=5)

    # Process recurring payments every 10 minutes
    scheduler.add_job(job_process_recurring_payments, "interval", minutes=10, args=[bot])

    # Daily reminder at 21:00 Dushanbe time
    scheduler.add_job(job_daily_evening_reminder, "cron", hour=21, minute=0, args=[bot])

    scheduler.start()
    logger.info("APScheduler initialized successfully.")
