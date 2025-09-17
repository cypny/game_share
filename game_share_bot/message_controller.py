from aiogram import Bot, Dispatcher, types
dp = Dispatcher()
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer("я бот")
async def start_listening(bot):
    await dp.start_polling(bot)
async def comand_i():
    # TODO
    pass
async def comand_games():
    # TODO
    pass
async def comand_start():
    # TODO посмотри на модель юзера и выведи необходимые данные для его заполнения
    pass