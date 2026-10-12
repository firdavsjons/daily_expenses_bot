import asyncio
import logging
import subprocess
import tempfile
import threading
import time
from pathlib import Path

from aiogram import F, Router
from aiogram.types import Message
from faster_whisper import WhisperModel

from bot.database import AsyncSessionLocal
from bot.handlers.transactions import handle_transaction_text
from bot.models import User
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = Router()

WHISPER_MODEL_SIZE = "small"
_whisper_model: WhisperModel | None = None
_whisper_model_lock = threading.Lock()


def _get_whisper_model() -> WhisperModel:
    global _whisper_model
    if _whisper_model is None:
        with _whisper_model_lock:
            if _whisper_model is None:
                logger.info("Loading local faster-whisper model: %s", WHISPER_MODEL_SIZE)
                _whisper_model = WhisperModel(
                    WHISPER_MODEL_SIZE,
                    device="cpu",
                    compute_type="int8",
                )
    return _whisper_model


def _transcribe_sync(audio_path: str, language: str | None) -> str:
    model = _get_whisper_model()
    segments, info = model.transcribe(
        audio_path,
        language=language if language in {"ru", "en", "tj", "uz"} else None,
        vad_filter=True,
    )
    text = " ".join(segment.text.strip() for segment in segments).strip()
    logger.info("Voice transcription detected language=%s text=%r", info.language, text)
    return text


async def _convert_to_wav(source_path: Path, target_path: Path) -> None:
    process = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y", "-i", str(source_path),
        "-ac", "1", "-ar", "16000", "-sample_fmt", "s16", str(target_path),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()
    if process.returncode != 0:
        details = stderr.decode("utf-8", errors="replace")[-500:]
        raise RuntimeError(f"ffmpeg conversion failed: {details}")


async def _user_language(telegram_id: int) -> str | None:
    async with AsyncSessionLocal() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
    return user.language if user else None


@router.message(F.voice)
async def handle_voice_message(message: Message):
    started_at = time.perf_counter()
    await message.answer("🎤 Распознаю голосовое сообщение...")

    try:
        telegram_file = await message.bot.get_file(message.voice.file_id)
        language = await _user_language(message.from_user.id)

        with tempfile.TemporaryDirectory(prefix="expenses_voice_") as temp_dir:
            source_path = Path(temp_dir) / "voice.ogg"
            wav_path = Path(temp_dir) / "voice.wav"
            await message.bot.download_file(telegram_file.file_path, destination=source_path)
            await _convert_to_wav(source_path, wav_path)
            recognized_text = await asyncio.to_thread(_transcribe_sync, str(wav_path), language)

        if not recognized_text:
            await message.answer("Не удалось разобрать голосовое сообщение. Попробуйте сказать ещё раз.")
            return

        elapsed = time.perf_counter() - started_at
        await message.answer(f"🎤 Распознано: «{recognized_text}»")
        logger.info("Voice message processed in %.2f seconds", elapsed)
        await handle_transaction_text(message, recognized_text)
    except Exception:
        logger.exception("Error processing voice message")
        await message.answer("⚠️ Не удалось обработать голосовое сообщение. Проверьте, что установлен ffmpeg.")