import asyncio
from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.domain.payment.yookassa_service import get_payment_status
from game_share_bot.infrastructure.models import Subscription
from game_share_bot.infrastructure.repositories import SubscriptionRepository
from game_share_bot.scheduler.job_container import job_container

logger = getLogger(__name__)

async def check_payment_polling(
        payment_id: str,
        max_attempts: int = 30):
    """
    Поллинг статуса платежа.
    Делает запросы каждые 5 секунд, пока не получит финальный статус или не кончатся попытки.
    """
    async with job_container.session_maker() as session:
        sub_repo = SubscriptionRepository(session)
        for attempt in range(max_attempts):
            try:
                status = await get_payment_status(payment_id)

                if status == "succeeded":
                    sub = await sub_repo.get_by_field("yookassa_payment_id", payment_id, options=[joinedload(Subscription.user)])
                    await _on_success(sub_repo, sub)
                    await session.commit()
                    return
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(5)

async def _on_success(sub_repo: SubscriptionRepository, sub_to_update: Subscription):
    await sub_repo.update(sub_to_update.id, status=SubscriptionStatus.ACTIVE)
    user_sub = await sub_repo.get_all_by_user(sub_to_update.user)
    for other_subscription in user_sub:
        if other_subscription.status == SubscriptionStatus.ACTIVE \
                and other_subscription.id != sub_to_update.id:
            await sub_repo.update(other_subscription.id, status=SubscriptionStatus.ENDED)

    try:
        await job_container.bot.send_message(
            sub_to_update.user.tg_id,
            f"✅ Ваша подписка {sub_to_update.plan.name} активирована до {sub_to_update.end_date.strftime('%d.%m.%Y')}."
        )
    except Exception as e:
        logger.warning(f"Не удалось отправить сообщение пользователю {sub_to_update.user.tg_id}: {e}")

    logger.info(f"Подписка {sub_to_update.id} активирована (оплата прошла)")