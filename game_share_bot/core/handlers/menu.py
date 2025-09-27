from aiogram import Router
from aiogram.types  import CallbackQuery

from game_share_bot.core.callbacks import MenuCallback
from game_share_bot.core.keyboards.inline import main_menu_kb

router = Router()

# TODO: может убрать MenuCallback и делать просто через строки
@router.callback_query(MenuCallback.filter())
async def handle_menu(callback: CallbackQuery, callback_data: MenuCallback):
    await callback.answer()
    if callback_data.section == "subs":
        return
    elif callback_data.section == "main":
        await callback.message.answer("Главное меню", reply_markup=main_menu_kb())
