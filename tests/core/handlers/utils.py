from aiogram.types import Message, CallbackQuery


async def respond_user(event: Message | CallbackQuery, text: str, markup=None):
    if isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=markup)