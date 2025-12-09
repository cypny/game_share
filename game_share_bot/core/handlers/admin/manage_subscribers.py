from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.keyboards import return_to_admin_main_panel_kb
from game_share_bot.core.services.admin import format_subscriber_message, format_subscriptions_message
from game_share_bot.core.states.admin.manage_subscribers import ManageSubscribersState
from game_share_bot.domain.enums import AdminAction
from game_share_bot.infrastructure.repositories import SubscriptionRepository, UserRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter_by_action(AdminAction.MANAGE_SUBSCRIBERS), IsAdmin())
async def manage_subscribers_panel(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    repo = SubscriptionRepository(session)
    subscriptions = await repo.get_all_active()
    await callback.message.edit_text(
        format_subscriptions_message(subscriptions), reply_markup=return_to_admin_main_panel_kb()
    )
    await state.set_state(ManageSubscribersState.waiting_for_user_phone)


@router.message(ManageSubscribersState.waiting_for_user_phone, IsAdmin())
async def manage_subscriber(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    subs_repo = SubscriptionRepository(session)
    user_repo = UserRepository(session)
    user = await user_repo.get_by_phone(message.text)

    if user is None:
        await message.answer(
            "Не удалось найти пользователя с таким номером(", reply_markup=return_to_admin_main_panel_kb()
        )
        return

    subscriptions = await subs_repo.get_all_by_user(user)
    if not subscriptions:
        await message.answer("У данного пользователя не было подписок", reply_markup=return_to_admin_main_panel_kb())
        return

    await message.answer(format_subscriber_message(subscriptions), reply_markup=return_to_admin_main_panel_kb())
