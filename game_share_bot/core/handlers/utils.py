from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from game_share_bot.core.keyboards import return_to_admin_main_panel_kb


async def respond_user(event: Message | CallbackQuery, text: str, markup=None):
    if isinstance(event, CallbackQuery):
        await event.answer()
        message = event.message

        if message.content_type == 'text':
            await message.edit_text(text, reply_markup=markup)
        else:
            # Нельзя через редактирование удалить фото
            await event.message.answer(text, reply_markup=markup)
    else:
        await event.answer(text, reply_markup=markup)


async def cancel_admin_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Действие отменено", reply_markup=return_to_admin_main_panel_kb())
