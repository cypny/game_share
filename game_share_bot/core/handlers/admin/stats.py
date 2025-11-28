from datetime import datetime, timezone

from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import AdminCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.keyboards import return_to_admin_main_panel_kb
from game_share_bot.domain.enums import AdminAction
from game_share_bot.infrastructure.models import Subscription, Disc, Rental, Game
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


async def _get_active_subscribers_count(session: AsyncSession) -> int:
    now = datetime.now(timezone.utc)
    stmt = select(func.count(func.distinct(Subscription.user_id))).where(Subscription.end_date >= now)
    result = await session.execute(stmt)
    value = result.scalar()
    return int(value or 0)


async def _get_discs_stats(session: AsyncSession) -> tuple[int, int]:
    total_stmt = select(func.count(Disc.disc_id))
    total_result = await session.execute(total_stmt)
    total_discs = int(total_result.scalar() or 0)

    rented_stmt = select(func.count(func.distinct(Rental.disc_id))).where(Rental.actual_end_date.is_(None))
    rented_result = await session.execute(rented_stmt)
    rented_discs = int(rented_result.scalar() or 0)

    available_discs = max(total_discs - rented_discs, 0)
    return rented_discs, available_discs


async def _get_popular_games(session: AsyncSession, limit: int = 10) -> list[tuple[str, int]]:
    stmt = (
        select(Game.title, func.count(Rental.id).label("rentals_count"))
        .join(Disc, Disc.game_id == Game.id)
        .join(Rental, Rental.disc_id == Disc.disc_id)
        .where(Rental.actual_end_date.is_(None))
        .group_by(Game.id, Game.title)
        .order_by(func.count(Rental.id).desc(), Game.title)
        .limit(limit)
    )
    result = await session.execute(stmt)
    rows = result.all()
    return [(row[0], int(row[1])) for row in rows]


def _format_stats_message(
    active_subscribers: int,
    rented_discs: int,
    available_discs: int,
    top_games: list[tuple[str, int]],
) -> str:
    lines = [
        "📊 Статистика сервиса",
        "",
        f"👥 Активные подписчики: {active_subscribers}",
        f"💿 Дисков в аренде: {rented_discs}",
        f"📀 Доступных дисков: {available_discs}",
        "",
        "🔥 Популярные игры:",
    ]

    if not top_games:
        lines.append("Пока нет арендованных игр.")
    else:
        for index, (title, count) in enumerate(top_games, start=1):
            lines.append(f"{index}. {title} — {count} активных аренд")

    return "\n".join(lines)


@router.callback_query(AdminCallback.filter_by_action(AdminAction.VIEW_STATS), IsAdmin())
async def show_stats(callback: CallbackQuery, session: AsyncSession):
    admin_id = callback.from_user.id
    logger.info(f"Администратор {admin_id} запросил статистику сервиса")

    try:
        active_subscribers = await _get_active_subscribers_count(session)
        rented_discs, available_discs = await _get_discs_stats(session)
        top_games = await _get_popular_games(session)

        text = _format_stats_message(
            active_subscribers=active_subscribers,
            rented_discs=rented_discs,
            available_discs=available_discs,
            top_games=top_games,
        )

        await callback.message.edit_text(text, reply_markup=return_to_admin_main_panel_kb())
        await callback.answer()
        logger.info(f"Статистика успешно отправлена администратору {admin_id}")
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {str(e)}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке статистики")
