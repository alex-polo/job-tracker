from typing import TYPE_CHECKING

from aiogram.enums import ParseMode
from aiogram.filters import Command

if TYPE_CHECKING:
    from aiogram import Dispatcher
    from aiogram.types import Message


async def command_start_handler(message: Message) -> None:
    """Handle the /start command.

    This handler is called when a user sends the /start command to the bot.
    It responds with a greeting message and the user's Telegram ID.

    Args:
        message: The incoming message object containing user information.
    """
    if not message.from_user:
        response_text: str = "<b>Hello!</b>\nUnable to retrieve your ID."
    else:
        user_id: int = message.from_user.id

        response_text: str = (
            f"<b>Hello!</b> I'm a job tracker bot.\n"
            f"Your ID: {user_id}.\n"
            f"Contact the administrator."
        )

    await message.answer(
        response_text,
        parse_mode=ParseMode.HTML,
    )


def register_commands(dp: Dispatcher) -> None:
    """Register command handlers with the dispatcher.

    This function registers all command handlers with the
    provided Dispatcher instance using the Command filter.

    Args:
        dp: The aiogram Dispatcher instance to register handlers with.

    """
    dp.message.register(command_start_handler, Command("start"))


__all__ = ("register_commands",)
