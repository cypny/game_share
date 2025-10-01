from aiogram import Router
from aiogram.types import CallbackQuery

from game_share_bot.core.callbacks import MenuCallback
from game_share_bot.core.keyboards.inline import main_menu_kb
from game_share_bot.core.logging import get_logger

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
        await callback.message.answer("Главное меню", reply_markup=main_menu_kb())
        logger.debug(f"Главное меню отправлено пользователю {user_id}")
