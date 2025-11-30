from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.testing.plugin.plugin_base import options

from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.keyboards import return_kb
from game_share_bot.core.keyboards.inline.admin import send_notification_kb
from game_share_bot.core.states.admin.create_notification import CreateNotificationState
from game_share_bot.domain.enums import AdminAction, SubscriptionAction
from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.infrastructure.models import Subscription
from game_share_bot.infrastructure.repositories import UserRepository, SubscriptionRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)

@router.callback_query(AdminCallback.filter_by_action(AdminAction.CREATE_NOTIFICATION), IsAdmin())
async def create_notification(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateNotificationState.waiting_for_message)
    await callback.answer()
    await callback.message.edit_text(
        text="Введите текст рассылки",
    )

@router.message(CreateNotificationState.waiting_for_message, IsAdmin())
async def process_notification_text(message: Message, state: FSMContext):
    notification_text = message.text
    await state.update_data({"notification_text": notification_text})
    await message.answer(
        text=(
            "Текст рассылки: \n"
            f"<i>{notification_text}</i>\n\n"
            "Подтвердите отправку"
        ),
        reply_markup=send_notification_kb(),
        parse_mode="html",
    )

@router.callback_query(AdminCallback.filter_by_action(AdminAction.SEND_NOTIFICATION_TO_ALL), IsAdmin())
async def send_notification_to_all(callback: CallbackQuery, session: AsyncSession, state: FSMContext, bot: Bot):
    await callback.answer()
    user_repo = UserRepository(session)
    notification_text = await state.get_value("notification_text")
    users = await user_repo.get_all()

    for user in users:
        try:
            await bot.send_message(
                chat_id=user.tg_id,
                text=notification_text,
            )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user.tg_id}", exc_info=True)

    await callback.message.edit_text(
        text=("Успешно отправлена рассылка с текстом:\n"
              f"<i>{notification_text}</i>"),
        reply_markup=return_kb(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL)),
        parse_mode="html",
    )
    await state.clear()

@router.callback_query(AdminCallback.filter_by_action(AdminAction.SEND_NOTIFICATION_TO_ACTIVE), IsAdmin())
async def send_notification_to_active(callback: CallbackQuery, session: AsyncSession, state: FSMContext, bot: Bot):
    await callback.answer()
    sub_repo = SubscriptionRepository(session)
    notification_text = await state.get_value("notification_text")
    subs = await sub_repo.get_all_by_field(
        "status",
        SubscriptionStatus.ACTIVE,
        options=[selectinload(Subscription.user)])

    user_ids = set(sub.user.tg_id for sub in subs)
    for user_id in user_ids:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=notification_text,
            )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user_id}", exc_info=True)

    await callback.message.edit_text(
        text=("Успешно отправлена рассылка с текстом:\n"
              f"<i>{notification_text}</i>"),
        reply_markup=return_kb(AdminCallback(action=AdminAction.RETURN_TO_MAIN_PANEL)),
        parse_mode="html",
    )
    await state.clear()
