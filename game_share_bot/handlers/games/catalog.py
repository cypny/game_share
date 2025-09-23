from aiogram import Router, F
from aiogram.types  import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from callbacks import MenuCallback
from infrastructure.repositories import GameRepository
from keyboards.inline import main_menu, catalog
from models import Game

router = Router()

@router.callback_query(F.data == "catalog")
async def handle_menu(callback: CallbackQuery, session: AsyncSession):
    game_repo = GameRepository(session)
    games = await game_repo.get_all()

    reply = "Каталог (все игры пока что): \n" + "\n".join([game.title for game in games])

    await callback.answer()
    await callback.message.answer(reply, reply_markup=catalog())
