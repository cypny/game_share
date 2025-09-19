from aiogram import Router, types
from aiogram.types  import CallbackQuery
from keyboards.inline import main_menu

router = Router()

@router.callback_query(lambda c: c.data.startswith("menu_"))
async def menu_callback(callback: CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "games":
        await callback.message.answer("Cписок игр")
    elif action == "orders":
        await callback.message.answer("Ваши подписки")

    await callback.answer()
