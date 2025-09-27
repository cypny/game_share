from aiogram import Router, F, types
from aiogram.types  import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.infrastructure.repositories import GameRepository
from game_share_bot.core.keyboards.inline import catalog_kb
from game_share_bot.infrastructure.utils.formatting import format_game_full, format_game_short, format_games_list

router = Router()

@router.callback_query(F.data == "catalog")
async def catalog(callback: CallbackQuery, session: AsyncSession):
    game_repo = GameRepository(session)

    games = await game_repo.get_all()
    games_str = "\n\n---\n\n".join(format_game_short(game) for game in games)
    reply = "Каталог (все игры пока что): \n" + games_str

    await callback.answer()
    await callback.message.answer(reply, parse_mode="HTML", reply_markup=catalog_kb())

@router.message(F.text.startswith("/game_"))
async def cmd_game(message: types.Message, session: AsyncSession):
    game_repo = GameRepository(session)

    game_id = int(message.text.split('_')[1])
    game = await game_repo.get_by_id(game_id)
    if game is None:
        await message.answer("Игра не найдена")
    reply = format_game_full(game)
    await message.answer_photo(
        caption=reply,
        parse_mode="HTML",
        photo=game.cover_image_url
    )

