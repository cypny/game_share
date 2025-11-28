from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import MenuCallback
from game_share_bot.domain.enums import MenuSection
from game_share_bot.infrastructure.repositories import UserRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)

HISTORY_PAGE_SIZE = 10


@router.callback_query(F.data.startswith("rental_history:"))
async def rentals_history_page(callback: CallbackQuery, session: AsyncSession):
    try:
        _, page_str = callback.data.split(":", maxsplit=1)
        page = int(page_str)
    except Exception:
        page = 0

    await _show_rentals_history(callback, session, page)


async def _show_rentals_history(callback: CallbackQuery, session: AsyncSession, page: int):
    user_tg_id = callback.from_user.id
    logger.info(f"Пользователь {user_tg_id} просматривает историю аренд, страница {page + 1}")

    user_repo = UserRepository(session)
    user = await user_repo.get_by_tg_id(user_tg_id)

    if not user:
        await callback.answer("❌ Пользователь не найден")
        return

    rentals = _get_sorted_rentals(list(user.rentals))
    total_rentals = len(rentals)

    if total_rentals == 0:
        text = "📜 История аренд пуста"
        markup = _history_keyboard(page=0, total_pages=1)
        await callback.answer()
        await callback.message.edit_text(text, reply_markup=markup)
        return

    total_pages = (total_rentals + HISTORY_PAGE_SIZE - 1) // HISTORY_PAGE_SIZE
    if page < 0:
        page = 0
    if page > total_pages - 1:
        page = total_pages - 1

    start = page * HISTORY_PAGE_SIZE
    end = start + HISTORY_PAGE_SIZE
    page_rentals = rentals[start:end]

    lines = [_format_rental_line(r) for r in page_rentals]
    lines_text = "\n".join(lines)

    text = f"📜 История аренд ({page + 1}/{total_pages}):\n\n{lines_text}"
    markup = _history_keyboard(page, total_pages)

    await callback.answer()
    await callback.message.edit_text(text, reply_markup=markup)


def _get_sorted_rentals(rentals: list) -> list:
    def sort_key(r):
        date = getattr(r, "start_date", None) or getattr(r, "created_at", None)
        return date

    return sorted(rentals, key=sort_key, reverse=True)


def _format_rental_line(rental) -> str:
    disc = getattr(rental, "disc", None)
    game = getattr(disc, "game", None) if disc else None
    game_title = getattr(game, "title", None) or "Без названия"

    start_value = getattr(rental, "start_date", None) or getattr(rental, "created_at", None)
    start_date = _format_date(start_value)

    end_value = getattr(rental, "actual_end_date", None)
    if end_value:
        end_date = _format_date(end_value)
    else:
        end_date = "диск еще не сдавали"

    return f"{game_title} | {start_date} - {end_date}"


def _format_date(dt) -> str:
    if not dt:
        return "-"
    return dt.strftime("%d.%m.%Y")


def _history_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []

    nav_buttons: list[InlineKeyboardButton] = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"rental_history:{page - 1}"
            )
        )
    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"rental_history:{page + 1}"
            )
        )

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ В личный кабинет",
                callback_data=MenuCallback(section=MenuSection.PERSONAL_CABINET).pack()
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
