from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.keyboards import return_to_admin_main_panel_kb
from game_share_bot.infrastructure.models import Game
from game_share_bot.infrastructure.repositories import GameRepository, DiscRepository
from game_share_bot.infrastructure.repositories.game_category import GameCategoryRepository
from game_share_bot.infrastructure.utils.formatting import format_game_text_full


async def respond_user(event: Message | CallbackQuery, text: str, markup=None) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer()
        message = event.message

        if message.content_type == "text":
            await message.edit_text(text, reply_markup=markup)
        else:
            # Нельзя через редактирование удалить фото
            await event.message.answer(text, reply_markup=markup)
    else:
        await event.answer(text, reply_markup=markup)


async def cancel_admin_action(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Действие отменено", reply_markup=return_to_admin_main_panel_kb())


async def get_list_of_categories_message(session: AsyncSession) -> str:
    categories = await GameCategoryRepository(session).get_all()
    result = ""
    for category in categories:
        result += f"{category.name}, "
    return result[:-2]


def get_game_adding_confirmation_text(data: dict[str, Any]) -> str:
    return f"Подтвердите добавление игры:\n\n{format_game_text_full(
        data["title"],
        data["description"],
        data["discs_count"],
        data["categories"]
    )}"


async def add_game(session: AsyncSession, data: dict[str, Any]) -> Game | None:
    game = await GameRepository(session).try_create(
        data["title"], data["description"], data["categories"], data["image"]
    )
    if game is None:
        return None
    disc_repo = DiscRepository(session)
    for _ in range(data["discs_count"]):
        await disc_repo.add_disc(game.id)
    return game

