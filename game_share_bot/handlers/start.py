from aiogram import Router, types
from aiogram.filters import CommandStart

from keyboards.inline import main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("/start command", reply_markup=main_menu())


