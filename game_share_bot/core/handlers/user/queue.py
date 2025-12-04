from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import MenuCallback, RentalCallback, TakeDiscConfirmationCallback
from game_share_bot.core.keyboards import take_disc_confirmation_kb
from game_share_bot.core.keyboards.inline.queue_page import my_queue_kb
from game_share_bot.core.states import TakeDiscState
from game_share_bot.domain.enums import MenuSection, RentalStatus
from game_share_bot.infrastructure.repositories import UserRepository, RentalRepository
from game_share_bot.infrastructure.repositories.rental.queue_entry import QueueEntryRepository
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.infrastructure.utils.formatting.queue import format_my_queue

router = Router()
logger = get_logger(__name__)

@router.callback_query(MenuCallback.filter_by_section(MenuSection.QUEUE))
async def my_queue(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user_repo = UserRepository(session)
    queue_repo = QueueEntryRepository(session)

    await callback.answer()
    await state.clear()  # Очищаем состояние при возврате в очередь

    user = await user_repo.get_by_tg_id(callback.from_user.id)
    if not user:
        await callback.message.edit_text("Пользователь не найден")
        return

    queues_info = await queue_repo.get_all_user_queues_full_info(user.id)

    pending_take = [rental for rental in user.rentals if rental.status_id == RentalStatus.PENDING_TAKE]

    message_text = format_my_queue(queues_info, pending_take)

    await callback.message.edit_text(
        text=message_text,
        parse_mode="HTML",
        reply_markup=my_queue_kb(pending_take),
    )


@router.callback_query(RentalCallback.filter(F.action == "take"))
async def request_take_disc_confirmation(callback: CallbackQuery, callback_data: RentalCallback, session: AsyncSession, state: FSMContext):
    """Запрашивает подтверждение взятия диска"""
    user_id = callback.from_user.id
    rental_id = callback_data.rental_id

    logger.info(f"Пользователь {user_id} запрашивает взятие диска по аренде {rental_id}")

    try:
        rental_repo = RentalRepository(session)
        rental = await rental_repo.get_by_id_with_relations(rental_id)

        if not rental:
            await callback.answer("❌ Аренда не найдена")
            return

        if rental.user_id != (await UserRepository(session).get_by_tg_id(user_id)).id:
            await callback.answer("❌ Это не ваша аренда")
            return

        if rental.status_id != RentalStatus.PENDING_TAKE:
            await callback.answer("❌ Диск уже взят или возвращен")
            return

        game_title = rental.disc.game.title

        # Сохраняем rental_id в состоянии
        await state.update_data(rental_id=rental_id)
        await state.set_state(TakeDiscState.waiting_for_confirmation)

        await callback.message.edit_text(
            f"🎮 <b>{game_title}</b>\n\n"
            f"❓ Вы точно взяли диск?\n\n"
            f"⚠️ Пожалуйста, подтвердите только после того, как физически забрали диск.",
            parse_mode="HTML",
            reply_markup=take_disc_confirmation_kb(rental_id)
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при запросе взятия диска: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при запросе взятия диска")


@router.callback_query(TakeDiscState.waiting_for_confirmation, TakeDiscConfirmationCallback.filter_confirmed())
async def confirm_take_disc(callback: CallbackQuery, callback_data: TakeDiscConfirmationCallback, session: AsyncSession, state: FSMContext):
    """Подтверждает взятие диска"""
    user_id = callback.from_user.id
    rental_id = callback_data.rental_id

    logger.info(f"Пользователь {user_id} подтверждает взятие диска по аренде {rental_id}")

    try:
        rental_repo = RentalRepository(session)

        # Дополнительная проверка
        rental = await rental_repo.get_by_id_with_relations(rental_id)
        if not rental:
            await callback.answer("❌ Аренда не найдена")
            await state.clear()
            return

        success = await rental_repo.confirm_take(rental_id)
        if not success:
            await callback.answer("❌ Ошибка при взятии")
            await state.clear()
            return

        await callback.answer("✅ Вы успешно взяли диск!")
        logger.info(f"Пользователь {user_id} успешно взял диск по аренде {rental_id}")

        await state.clear()
        await my_queue(callback, session, state)

    except Exception as e:
        logger.error(f"Ошибка при подтверждении взятия диска: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при взятии диска")
        await state.clear()


@router.callback_query(TakeDiscState.waiting_for_confirmation, TakeDiscConfirmationCallback.filter_canceled())
async def cancel_take_disc(callback: CallbackQuery, callback_data: TakeDiscConfirmationCallback, session: AsyncSession, state: FSMContext):
    """Отменяет взятие диска"""
    user_id = callback.from_user.id
    rental_id = callback_data.rental_id

    logger.info(f"Пользователь {user_id} отменил взятие диска по аренде {rental_id}")

    await callback.answer("❌ Взятие диска отменено")
    await state.clear()
    await my_queue(callback, session, state)
