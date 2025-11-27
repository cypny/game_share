from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import AdminCallback, RentalCallback
from game_share_bot.core.keyboards import rental_actions_confirmation_kb, return_to_admin_main_panel_kb
from game_share_bot.domain.enums import AdminAction, RentalStatus
from game_share_bot.infrastructure.models import Rental
from game_share_bot.infrastructure.repositories import RentalRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


def _format_pending_returns_message(rentals: list[Rental]) -> str:
    """Форматирует сообщение со списком запросов на возврат"""
    if not rentals:
        return "📋 Запросы на возврат отсутствуют"

    returns_list = []
    for rental in rentals:
        user_info = f"👤 @{rental.user.name} (ID: {rental.user.tg_id})"
        game_info = f"🎮 {rental.disc.game.title} - Диск {rental.disc.disc_id}"
        return_info = f"📅 Начало аренды: {rental.start_date.strftime('%d.%m.%Y')}"

        full_info = f"{user_info}\n{game_info}\n{return_info}"
        returns_list.append(full_info)

    returns_str = "\n\n".join(returns_list)
    return f"📋 Запросы на возврат ({len(rentals)}):\n\n{returns_str}"


@router.callback_query(AdminCallback.filter_by_action(AdminAction.VIEW_RETURN_REQUESTS))
async def show_return_requests(callback: CallbackQuery, session: AsyncSession):
    """Показывает все запросы на возврат для администратора"""
    user_id = callback.from_user.id
    logger.info(f"Администратор {user_id} запросил список запросов на возврат")

    try:
        rental_repo = RentalRepository(session)
        pending_returns = await rental_repo.get_rentals_by_status(RentalStatus.PENDING_RETURN)

        text = _format_pending_returns_message(pending_returns)
        markup = rental_actions_confirmation_kb(pending_returns,
                                                "return") if pending_returns else return_to_admin_main_panel_kb()

        await callback.message.edit_text(text, reply_markup=markup)
        logger.info(f"Список запросов на возврат отправлен администратору {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при получении запросов на возврат: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке запросов на возврат")


@router.callback_query(RentalCallback.filter(F.action == "confirm_return"))
async def confirm_return_request(callback: CallbackQuery, callback_data: RentalCallback, session: AsyncSession):
    """Подтверждает возврат диска администратором"""
    admin_id = callback.from_user.id
    rental_id = callback_data.rental_id

    logger.info(f"Администратор {admin_id} подтверждает возврат аренды {rental_id}")

    try:
        rental_repo = RentalRepository(session)
        success = await rental_repo.confirm_return(rental_id)

        if not success:
            await callback.answer("❌ Ошибка при подтверждении возврата")
            return

        await callback.answer("✅ Возврат успешно подтвержден!")
        await show_return_requests(callback, session)
        logger.info(f"Администратор {admin_id} подтвердил возврат аренды {rental_id}")

    except Exception as e:
        logger.error(f"Ошибка при подтверждении возврата: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при подтверждении возврата")


@router.callback_query(RentalCallback.filter(F.action == "reject_return"))
async def reject_return_request(callback: CallbackQuery, callback_data: RentalCallback, session: AsyncSession):
    """Отклоняет возврат диска администратором"""
    admin_id = callback.from_user.id
    rental_id = callback_data.rental_id

    logger.info(f"Администратор {admin_id} отклоняет возврат аренды {rental_id}")

    try:
        rental_repo = RentalRepository(session)
        success = await rental_repo.reject_return(rental_id)

        if not success:
            await callback.answer("❌ Ошибка при отклонении возврата")
            return

        await callback.answer("❌ Возврат отклонен")
        await show_return_requests(callback, session)
        logger.info(f"Администратор {admin_id} отклонил возврат аренды {rental_id}")

    except Exception as e:
        logger.error(f"Ошибка при отклонении возврата: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при отклонении возврата")
