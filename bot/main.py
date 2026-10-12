import asyncio
import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from bot import config
from bot.database import ensure_database_exists, AsyncSessionLocal
from bot.seed import seed_default_categories
from bot.services.currency_service import fetch_and_update_rates
from bot.services.scheduler import setup_scheduler
from bot.services.telegram_session import ResilientAiohttpSession

from bot.handlers import admin, start, transactions, voice, undo, categories, reports, budgets, currency, recurring

# Setup logging
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
file_handler = RotatingFileHandler(
    LOG_DIR / "bot.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8",
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), file_handler]
)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    """
    Startup tasks: DB connection check, seeding defaults, rates update, scheduler setup.
    Note: Alembic migrations are executed separately via 'alembic upgrade head' CLI.
    """
    logger.info("Initializing expenses_bot backend...")

    # 1. Ensure database connection
    await ensure_database_exists()

    # 2. Seed default categories & exchange rates
    async with AsyncSessionLocal() as session:
        await seed_default_categories(session)
        await fetch_and_update_rates(session)

    # 3. Initialize scheduler
    setup_scheduler(bot)

    logger.info("Startup initialization completed.")

async def main():
    token = config.TELEGRAM_BOT_TOKEN
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.warning(
            "⚠️ TELEGRAM_BOT_TOKEN is missing or default in .env file! "
            "Please set a valid bot token in .env to connect to Telegram."
        )

    # Initialize bot and dispatcher
    bot = Bot(
        token=token if token else "7777777777:AAA_DEMO_TOKEN_PLACEHOLDER",
        session=ResilientAiohttpSession(),
    )
    dp = Dispatcher()

    # Include handler routers (specific command/button routers first, fallback free text transaction router last)
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(categories.router)
    dp.include_router(reports.router)
    dp.include_router(budgets.router)
    dp.include_router(currency.router)
    dp.include_router(recurring.router)
    dp.include_router(voice.router)
    dp.include_router(undo.router)
    dp.include_router(transactions.router)

    # Run startup callback
    await on_startup(bot)

    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.info("Initialization & migrations verified cleanly. Bot awaiting valid TELEGRAM_BOT_TOKEN to poll.")
        return

    logger.info("Bot starting polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
