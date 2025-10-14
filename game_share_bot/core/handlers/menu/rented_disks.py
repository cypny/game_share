from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import MenuCallback, RentalCallback
from game_share_bot.core.keyboards.inline import return_kb
from game_share_bot.infrastructure.repositories import RentalRepository, DiscRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


def _format_rented_disks_message(rentals: list) -> str:
    """Форматирует сообщение со списком арендованных дисков"""
    if not rentals:
        return "📦 У вас нет арендованных дисков"

    disks_list = []
    for rental in rentals:
        game_title = rental.disc.game.title
        disk_info = f"🎮 {game_title} - экземпляр {rental.disc.disc_id}"
        disks_list.append(disk_info)

    disks_str = "\n\n".join(disks_list)
    return f"📦 Ваши арендованные диски:\n\n{disks_str}"


def _create_rentals_keyboard(rentals: list) -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками возврата для каждого диска"""
    keyboard_buttons = []

    for rental in rentals:
        button_text = f"🔙 Вернуть {rental.disc.game.title}"
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=RentalCallback(action="return", rental_id=rental.id).pack()
            )
        ])

    keyboard_buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=MenuCallback(section='personal').pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


async def _get_user_rentals(user_id: int, session: AsyncSession) -> list:
    """Получает список активных аренд пользователя"""
    rental_repo = RentalRepository(session)
    return await rental_repo.get_active_rentals_by_user(user_id)


@router.callback_query(MenuCallback.filter(F.section == "rented_disks"))
async def show_rented_disks(callback: CallbackQuery, session: AsyncSession):
    """Показывает все арендованные диски пользователя"""
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} запросил список арендованных дисков")

    try:
        rentals = await _get_user_rentals(user_id, session)
        text = _format_rented_disks_message(rentals)
        markup = _create_rentals_keyboard(rentals) if rentals else return_kb(MenuCallback(section='personal'))

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
    """Обрабатывает возврат диска и обновляет статусы"""
    rental_repo = RentalRepository(session)
    disc_repo = DiscRepository(session)

    try:
        rental = await rental_repo.get_by_id_with_disc(rental_id)
        if not rental:
            return False

        success_rental = await rental_repo.update_rental_status(rental_id, 2)
        success_disc = await disc_repo.update_disc_status(rental.disc_id, 1)

        return success_rental and success_disc
    except Exception as e:
        logger.error(f"Ошибка при обработке возврата диска: {str(e)}")
        return False


@router.callback_query(RentalCallback.filter(F.action == "return"))
async def return_disk(callback: CallbackQuery, callback_data: RentalCallback, session: AsyncSession):
    """Обрабатывает возврат арендованного диска"""
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
            await callback.answer("❌ Ошибка при возврате диска")
            return

        await callback.answer(f"✅ Диск '{game_title}' успешно возвращен!")
        await show_rented_disks(callback, session)
        logger.info(f"Пользователь {user_id} успешно вернул диск {rental_id}")

    except Exception as e:
        logger.error(f"Ошибка при возврате диска: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при возврате диска")