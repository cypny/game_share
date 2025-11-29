from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from game_share_bot.infrastructure.models import Subscription
from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.scheduler.job_container import job_container

logger = get_logger(__name__)

async def notify_subscription_end():
    try:
        async with job_container.session_maker() as session:
            today = datetime.now(timezone.utc).date()
            tomorrow = today + timedelta(days=1)
            week_later = today + timedelta(days=7)

            base_query = (
                select(Subscription)
                .options(
                    selectinload(Subscription.user)
                )
                .where(
                    Subscription.status==SubscriptionStatus.ACTIVE,
                )
            )

            q_tomorrow = base_query.where(func.date(Subscription.end_date) == tomorrow)
            subs_tomorrow = (await session.execute(q_tomorrow)).scalars().all()

            q_today = base_query.where(func.date(Subscription.end_date) == week_later)
            subs_week_later = (await session.execute(q_today)).scalars().all()

            bot = job_container.bot

            #TODO: возможность продления
            for sub in subs_tomorrow:
                await bot.send_message(
                    chat_id=sub.user.tg_id,
                    text=f"Напоминаем: подписка заканчивается завтра ({sub.end_date.strftime('%d.%m.%Y')})"
                )

            for sub in subs_week_later:
                await bot.send_message(
                    chat_id=sub.user.tg_id,
                    text=f"Напоминаем: подписка заканчивается через неделю ({sub.end_date.strftime('%d.%m.%Y')})"
                )

    except Exception as err:
        logger.error(err, exc_info=True)
        raise