import asyncio
import logging

from yookassa import Payment

from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.infrastructure.repositories import SubscriptionRepository
from game_share_bot.scheduler.job_container import job_container

logger = logging.getLogger(__name__)

async def check_pending_subscriptions():
    async with job_container.session_maker() as session:
        sub_repo = SubscriptionRepository(session)
        pending_subs = await sub_repo.get_all_pending()

        for sub in pending_subs:
            try:
                payment = await asyncio.to_thread(Payment.find_one, str(sub.yookassa_payment_id))
                status = payment.status

                if status == "succeeded":
                    await sub_repo.update(sub.id, status=SubscriptionStatus.ACTIVE)

                    try:
                        await job_container.bot.send_message(
                            sub.user.tg_id,
                            f"✅ Ваша подписка {sub.plan.name} активирована до {sub.end_date.strftime('%d.%m.%Y')}."
                        )
                    except Exception as e:
                        logger.warning(f"Не удалось отправить сообщение пользователю {sub.user.tg_id}: {e}")

                    logger.info(f"Подписка {sub.id} активирована (оплата прошла)")

                elif status in ("canceled", "expired"):
                    await sub_repo.update(sub.id, status=SubscriptionStatus.CANCELED_PAYMENT)
                    logger.info(f"Подписка {sub.id} отменена (статус {status})")

                else:
                    logger.debug(f"Подписка {sub.id} в статусе {status}, ждем оплаты")

            except Exception as e:
                logger.error(f"Ошибка при проверке подписки {sub.id}: {e}")
