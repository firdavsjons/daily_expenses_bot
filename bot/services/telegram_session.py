import asyncio
import logging

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.session.base import TelegramType
from aiogram.exceptions import TelegramNetworkError
from aiogram.methods import TelegramMethod

logger = logging.getLogger(__name__)


class ResilientAiohttpSession(AiohttpSession):
    """Retries transient network failures without repeating the handler."""

    max_attempts = 3

    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[TelegramType],
        timeout: int | None = None,
    ) -> TelegramType:
        for attempt in range(1, self.max_attempts + 1):
            try:
                return await super().make_request(bot, method, timeout)
            except TelegramNetworkError as error:
                if attempt == self.max_attempts:
                    raise

                delay = 2 ** (attempt - 1)
                logger.warning(
                    "Telegram API request failed (%s/%s): %s. Retrying in %ss.",
                    attempt,
                    self.max_attempts,
                    error,
                    delay,
                )
                await asyncio.sleep(delay)

        raise RuntimeError("Telegram request retry loop ended unexpectedly")