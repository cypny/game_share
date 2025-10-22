from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import MenuCallback, RentalCallback
from game_share_bot.core.keyboards import return_kb, rentals_kb
from game_share_bot.domain.enums import RentalStatus, DiscStatus, MenuSection
from game_share_bot.infrastructure.models import Rental
from game_share_bot.infrastructure.repositories import RentalRepository, DiscRepository
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.infrastructure.utils.formatting import format_rented_disks_message

router = Router()
logger = get_logger(__name__)


async def _get_user_rentals(user_id: int, session: AsyncSession) -> list[Rental]:
    """Получает список активных аренд пользователя"""
    rental_repo = RentalRepository(session)
    return await rental_repo.get_active_rentals_by_user(user_id)


@router.callback_query(MenuCallback.filter_by_section(MenuSection.RENTED_DISKS))
async def show_rented_disks(callback: CallbackQuery, session: AsyncSession):
    """Показывает все арендованные диски пользователя"""
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} запросил список арендованных дисков")

    try:
        rentals = await _get_user_rentals(user_id, session)
        text = format_rented_disks_message(rentals)
        markup = rentals_kb(rentals) if rentals else return_kb(MenuCallback(section=MenuSection.PERSONAL_CABINET))

        await callback.message.edit_text(text, reply_markup=markup)
        logger.info(f"Список арендованных дисков отправлен пользователю {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при получении арендованных дисков: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке списка дисков")


async def _validate_rental_return(rental_id: int, user_id: int, session: AsyncSession) -> tuple[bool, str]:
    """Проверяет возможность возврата аренды"""
    rental_repo = RentalRepository(session)
    rental = await rental_repo.get_by_id_with_relations(rental_id)

    if not rental:
        return False, "❌ Аренда не найдена"

    if rental.user.tg_id != user_id:
        return False, "❌ Это не ваш диск"

    return True, rental.disc.game.title


async def _process_disk_return(rental_id: int, session: AsyncSession) -> bool:
    """Обрабатывает запрос на возврат диска (ставит в ожидание подтверждения)"""
    rental_repo = RentalRepository(session)
    disc_repo = DiscRepository(session)

    try:
        rental = await rental_repo.get_by_id_with_disc(rental_id)
        if not rental:
            return False

        # Устанавливаем статус "ожидает подтверждения" для аренды и диска
        success_rental = await rental_repo.update_rental_status(rental_id, RentalStatus.PENDING_RETURN)
        success_disc = await disc_repo.update_disc_status(rental.disc_id, DiscStatus.PENDING_RETURN)

        return success_rental and success_disc
    except Exception as e:
        logger.error(f"Ошибка при обработке возврата диска: {str(e)}")
        return False


@router.callback_query(RentalCallback.filter(F.action == "return"))
async def return_disk(callback: CallbackQuery, callback_data: RentalCallback, session: AsyncSession):
    """Обрабатывает запрос на возврат арендованного диска"""
    user_id = callback.from_user.id
    rental_id = callback_data.rental_id

    logger.info(f"Пользователь {user_id} пытается вернуть диск по аренде {rental_id}")

    try:
        is_valid, game_title = await _validate_rental_return(rental_id, user_id, session)
        if not is_valid:
            await callback.answer(game_title)
            return

        success = await _process_disk_return(rental_id, session)
        if not success:
            await callback.answer("❌ Ошибка при запросе возврата диска")
            return

        await callback.answer(f"⏳ Запрос на возврат диска '{game_title}' отправлен администратору!")
        await show_rented_disks(callback, session)
        logger.info(f"Пользователь {user_id} запросил возврат диска {rental_id}")

    except Exception as e:
        logger.error(f"Ошибка при запросе возврата диска: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при запросе возврата диска")
