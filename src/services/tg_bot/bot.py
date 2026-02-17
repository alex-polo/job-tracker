from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher
from aiogram.filters import Command

if TYPE_CHECKING:
    from aiogram.types import Message

BOT_CONFIG = None

TOKEN = ""

dp = Dispatcher()


# Command handler
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    """Start command handler."""
    await message.answer("Hello! I'm a bot created with aiogram.")


# Run the bot
async def run_bot() -> None:
    """Run the bot."""
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)
