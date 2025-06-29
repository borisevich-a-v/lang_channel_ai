import asyncio
import logging
import sys
from os import getenv
from pathlib import Path

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types.base import TelegramObject
from typing import Any, Awaitable, Callable, Dict
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

TOKEN = getenv("BOT_TOKEN")
ALLOWED_USERS = [int(user_id) for user_id in getenv("ALLOWED_USERS", "").split(",") if user_id]


class AuthMiddleware:
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            if event.from_user.id not in ALLOWED_USERS:
                await event.answer("Sorry, you are not authorized to use this bot.")
                return
        return await handler(event, data)


dp = Dispatcher()
dp.message.middleware(AuthMiddleware())


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! I'm AI agent that helps you with th channel management.")


@dp.message()
async def ai_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
