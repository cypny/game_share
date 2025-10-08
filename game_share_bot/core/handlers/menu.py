from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from game_share_bot.core.callbacks import MenuCallback
from game_share_bot.core.keyboards import main_menu_kb
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


# TODO: может убрать MenuCallback и делать просто через строки
@router.callback_query(MenuCallback.filter())
async def handle_menu(callback: CallbackQuery, callback_data: MenuCallback):
    user_id = callback.from_user.id
    section = callback_data.section

    logger.info(f"Пользователь {user_id} выбрал раздел меню: {section}")

    await callback.answer()
    if callback_data.section == "subs":
        logger.debug(f"Запрошено меню подписок пользователем {user_id}")
        # TODO: реализовать подписки
        return
    elif callback_data.section == "main":
        await callback.message.edit_text("Главное меню", reply_markup=main_menu_kb())
        logger.debug(f"Главное меню отправлено пользователю {user_id}")


@router.callback_query(F.data == "help")
@router.message(Command("help"))
async def handle_help(callback: CallbackQuery | Message):
    kwargs = dict(
        text="@cynpy_the_best",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Меню", callback_data=MenuCallback(section="main").pack())]
            ]
        )
    )

    if isinstance(callback, Message):
        await callback.answer(**kwargs)
    elif isinstance(callback, CallbackQuery):
        await callback.answer()
        await callback.message.edit_text(**kwargs)
