from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from game_share_bot.core.keyboards import return_to_admin_panel_kb


async def respond_user(event: Message | CallbackQuery, text: str, markup=None):
    if isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=markup)
        await event.answer()


async def cancel_admin_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Действие отменено", reply_markup=return_to_admin_panel_kb())
