from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import AdminCallback, RentalCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.keyboards import rental_actions_confirmation_kb, return_to_admin_main_panel_kb
from game_share_bot.domain.enums import AdminAction, RentalStatus
from game_share_bot.infrastructure.repositories import RentalRepository
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.infrastructure.utils.formatting.rental import format_pending_take_message, format_rental_full

router = Router()
logger = get_logger(__name__)


@router.message(F.text.startswith("/rental_"), IsAdmin())
async def cmd_rental(message: Message, session: AsyncSession):
    rental_repo = RentalRepository(session)
    rental_id = int(message.text.split('_')[1])

    rental = await rental_repo.get_by_id(rental_id)

    await message.answer(
        text=format_rental_full(rental),
        parse_mode="HTML",
    )


@router.callback_query(AdminCallback.filter_by_action(AdminAction.VIEW_TAKE_REQUESTS), IsAdmin())
async def show_take_request(callback: RentalCallback, session: AsyncSession):
    user_id = callback.from_user.id
    logger.info(f"Администратор {user_id} запросил список запросов на возврат")

    try:
        rental_repo = RentalRepository(session)
        pending_takes = await rental_repo.get_rentals_by_status(RentalStatus.PENDING_TAKE)

        text = format_pending_take_message(pending_takes)
        markup = rental_actions_confirmation_kb(pending_takes, "take") if pending_takes else return_to_admin_main_panel_kb()

        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=markup
        )
        logger.info(f"Список запросов на получение отправлен администратору {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при получении запросов на получение: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке запросов на получение")


@router.callback_query(RentalCallback.filter(F.action == "confirm_take"))
async def confirm_return_request(callback: CallbackQuery, callback_data: RentalCallback, session: AsyncSession):
    """Подтверждает возврат диска администратором"""
    admin_id = callback.from_user.id
    rental_id = callback_data.rental_id

    logger.info(f"Администратор {admin_id} подтверждает взятие аренды {rental_id}")

    try:
        rental_repo = RentalRepository(session)
        success = await rental_repo.confirm_take(rental_id)

        if not success:
            await callback.answer("❌ Ошибка при подтверждении возврата")
            return

        await callback.answer("✅ Возврат успешно подтвержден!")
        await show_take_request(callback, session)
        logger.info(f"Администратор {admin_id} подтвердил возврат аренды {rental_id}")

    except Exception as e:
        logger.error(f"Ошибка при подтверждении возврата: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при подтверждении возврата")


@router.callback_query(RentalCallback.filter(F.action == "reject_take"))
async def reject_return_request(callback: CallbackQuery, callback_data: RentalCallback, session: AsyncSession):
    """Отклоняет взятие диска администратором"""
    admin_id = callback.from_user.id
    rental_id = callback_data.rental_id

    logger.info(f"Администратор {admin_id} отклоняет взятие аренды {rental_id}")

    try:
        rental_repo = RentalRepository(session)
        success = await rental_repo.reject_take(rental_id)

        if not success:
            await callback.answer("❌ Ошибка при отклонении взятия")
            return

        await callback.answer("❌ Взятие отклонено")
        await show_take_request(callback, session)
        logger.info(f"Администратор {admin_id} отклонил взятие аренды {rental_id}")

    except Exception as e:
        logger.error(f"Ошибка при отклонении взятия: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при отклонении взятия")
