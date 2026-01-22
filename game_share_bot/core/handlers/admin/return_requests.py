from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import AdminCallback, RentalCallback
from game_share_bot.core.keyboards import return_to_admin_main_panel_kb
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


def _format_single_return_message(rental: Rental, current_page: int, total_count: int) -> str:
    """Форматирует сообщение для одного запроса на возврат"""
    user_info = f"👤 @{rental.user.name} (ID: {rental.user.tg_id})"
    game_info = f"🎮 {rental.disc.game.title} - Диск {rental.disc.disc_id}"
    return_info = f"📅 Начало аренды: {rental.start_date.strftime('%d.%m.%Y')}"

    return (
        f"📋 Запрос на возврат ({current_page + 1}/{total_count}):\n\n"
        f"{user_info}\n"
        f"{game_info}\n"
        f"{return_info}"
    )


@router.callback_query(AdminCallback.filter_by_action(AdminAction.VIEW_RETURN_REQUESTS))
async def show_return_requests(callback: CallbackQuery, callback_data: AdminCallback, session: AsyncSession):
    """Показывает все запросы на возврат для администратора"""
    user_id = callback.from_user.id
    page = callback_data.page
    logger.info(f"Администратор {user_id} запросил список запросов на возврат (страница {page})")

    try:
        rental_repo = RentalRepository(session)
        pending_returns = await rental_repo.get_rentals_by_status(RentalStatus.PENDING_RETURN)

        if not pending_returns:
            text = "📋 Запросы на возврат отсутствуют"
            markup = return_to_admin_main_panel_kb()
            await callback.message.edit_text(text, reply_markup=markup)
            return

        # Проверяем валидность страницы
        if page >= len(pending_returns):
            page = 0

        current_rental = pending_returns[page]
        text = _format_single_return_message(current_rental, page, len(pending_returns))

        from game_share_bot.core.keyboards.inline.admin import rental_action_single_kb
        markup = rental_action_single_kb(
            current_rental,
            "return",
            page,
            len(pending_returns),
            AdminAction.VIEW_RETURN_REQUESTS
        )

        await callback.message.edit_text(text, reply_markup=markup)
        logger.info(f"Запрос на возврат ({page + 1}/{len(pending_returns)}) отправлен администратору {user_id}")

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

        # Показываем следующий запрос или возвращаемся к панели
        await show_return_requests(callback, AdminCallback(action=AdminAction.VIEW_RETURN_REQUESTS, page=0), session)
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

        # Показываем следующий запрос или возвращаемся к панели
        await show_return_requests(callback, AdminCallback(action=AdminAction.VIEW_RETURN_REQUESTS, page=0), session)
        logger.info(f"Администратор {admin_id} отклонил возврат аренды {rental_id}")

    except Exception as e:
        logger.error(f"Ошибка при отклонении возврата: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при отклонении возврата")


# === Обработчики для запросов на получение ===

def _format_pending_takes_message(rentals: list[Rental]) -> str:
    """Форматирует сообщение со списком запросов на получение"""
    if not rentals:
        return "📋 Запросы на получение отсутствуют"

    takes_list = []
    for rental in rentals:
        user_info = f"👤 @{rental.user.name} (ID: {rental.user.tg_id})"
        game_info = f"🎮 {rental.disc.game.title} - Диск {rental.disc.disc_id}"
        created_info = f"📅 Создан: {rental.start_date.strftime('%d.%m.%Y %H:%M')}"

        full_info = f"{user_info}\n{game_info}\n{created_info}"
        takes_list.append(full_info)

    takes_str = "\n\n".join(takes_list)
    return f"📋 Запросы на получение ({len(rentals)}):\n\n{takes_str}"


def _format_single_take_message(rental: Rental, current_page: int, total_count: int) -> str:
    """Форматирует сообщение для одного запроса на получение"""
    user_info = f"👤 @{rental.user.name} (ID: {rental.user.tg_id})"
    game_info = f"🎮 {rental.disc.game.title} - Диск {rental.disc.disc_id}"
    created_info = f"📅 Создан: {rental.start_date.strftime('%d.%m.%Y %H:%M')}"

    return (
        f"📋 Запрос на получение ({current_page + 1}/{total_count}):\n\n"
        f"{user_info}\n"
        f"{game_info}\n"
        f"{created_info}"
    )


@router.callback_query(AdminCallback.filter_by_action(AdminAction.VIEW_TAKE_REQUESTS))
async def show_take_requests(callback: CallbackQuery, callback_data: AdminCallback, session: AsyncSession):
    """Показывает все запросы на получение для администратора"""
    user_id = callback.from_user.id
    page = callback_data.page
    logger.info(f"Администратор {user_id} запросил список запросов на получение (страница {page})")

    try:
        rental_repo = RentalRepository(session)
        pending_takes = await rental_repo.get_rentals_by_status(RentalStatus.PENDING_TAKE)

        if not pending_takes:
            text = "📋 Запросы на получение отсутствуют"
            markup = return_to_admin_main_panel_kb()
            await callback.message.edit_text(text, reply_markup=markup)
            return

        # Проверяем валидность страницы
        if page >= len(pending_takes):
            page = 0

        current_rental = pending_takes[page]
        text = _format_single_take_message(current_rental, page, len(pending_takes))

        from game_share_bot.core.keyboards.inline.admin import rental_action_single_kb
        markup = rental_action_single_kb(
            current_rental,
            "take",
            page,
            len(pending_takes),
            AdminAction.VIEW_TAKE_REQUESTS
        )

        await callback.message.edit_text(text, reply_markup=markup)
        logger.info(f"Запрос на получение ({page + 1}/{len(pending_takes)}) отправлен администратору {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при получении запросов на получение: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке запросов на получение")


@router.callback_query(RentalCallback.filter(F.action == "confirm_take"))
async def confirm_take_request(callback: CallbackQuery, callback_data: RentalCallback, session: AsyncSession):
    """Подтверждает получение диска администратором"""
    admin_id = callback.from_user.id
    rental_id = callback_data.rental_id

    logger.info(f"Администратор {admin_id} подтверждает получение аренды {rental_id}")

    try:
        rental_repo = RentalRepository(session)
        success = await rental_repo.confirm_take(rental_id)

        if not success:
            await callback.answer("❌ Ошибка при подтверждении получения")
            return

        await callback.answer("✅ Получение успешно подтверждено!")

        # Показываем следующий запрос или возвращаемся к панели
        await show_take_requests(callback, AdminCallback(action=AdminAction.VIEW_TAKE_REQUESTS, page=0), session)
        logger.info(f"Администратор {admin_id} подтвердил получение аренды {rental_id}")

    except Exception as e:
        logger.error(f"Ошибка при подтверждении получения: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при подтверждении получения")


@router.callback_query(RentalCallback.filter(F.action == "reject_take"))
async def reject_take_request(callback: CallbackQuery, callback_data: RentalCallback, session: AsyncSession):
    """Отклоняет получение диска администратором"""
    admin_id = callback.from_user.id
    rental_id = callback_data.rental_id

    logger.info(f"Администратор {admin_id} отклоняет получение аренды {rental_id}")

    try:
        rental_repo = RentalRepository(session)
        rental = await rental_repo.get_by_id(rental_id)
        if not rental:
            await callback.answer("❌ Аренда не найдена")
            return

        # Отклоняем получение (можно добавить логику возврата в очередь)
        await callback.answer("❌ Получение отклонено")

        # Показываем следующий запрос или возвращаемся к панели
        await show_take_requests(callback, AdminCallback(action=AdminAction.VIEW_TAKE_REQUESTS, page=0), session)
        logger.info(f"Администратор {admin_id} отклонил получение аренды {rental_id}")

    except Exception as e:
        logger.error(f"Ошибка при отклонении получения: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при отклонении получения")
