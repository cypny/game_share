from aiogram import Router, types
from aiogram.filters import CommandStart

from core.keyboards.inline import main_menu_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("/start command", reply_markup=main_menu_kb())


