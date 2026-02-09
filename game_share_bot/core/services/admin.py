from aiogram.types import InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.domain.enums.subscription_status import SubscriptionStatus
from game_share_bot.infrastructure.models import Game, Subscription
from game_share_bot.infrastructure.models.game import GameCategory
from game_share_bot.infrastructure.repositories import GameRepository
from game_share_bot.infrastructure.repositories.game_category import GameCategoryRepository


async def try_get_game_by_id_in_message(
    message: Message, session: AsyncSession, return_kb: InlineKeyboardMarkup
) -> Game | None:
    try:
        game_id = int(message.text)
    except ValueError:
        await message.answer("ID должно быть числом", reply_markup=return_kb)
        return None

    game = await GameRepository(session).get_by_id(game_id)
    if game is None:
        await message.answer(f"Игра с ID = {game_id} не найдена", reply_markup=return_kb)
        return None

    return game


async def try_parse_categories(message_text: str, session: AsyncSession) -> list[GameCategory] | None:
    category_names = message_text.split(",")
    game_categories = []
    repo = GameCategoryRepository(session)
    for category_name in category_names:
        category = await repo.get_by_name(category_name)
        if category is None:
            return None
        game_categories.append(category)

    return game_categories if game_categories else None


def format_subscriptions_message(subscriptions: list[Subscription]) -> str:
    res = f"Всего активных подписчиков: {len(subscriptions)}\n\n"
    for subscription in subscriptions:
        res += f"{subscription.user.name} - {subscription.user.phone} - {subscription.plan.name}\n"
    res += "\nВведите номер телефона пользователя для получения подробной информации:"
    return res


def format_subscriber_message(user_subscriptions: list[Subscription], user: "User") -> str:
    is_active = any(user_subscription.status == SubscriptionStatus.ACTIVE for user_subscription in user_subscriptions)
    res = (
        f"Имя пользователя: {user.name}\n"
        f"Телефон пользователя: {user.phone}\n"
        f"Телеграмм ID пользователя: {user.tg_id}\n"
        f"Кол-во подписок: {len(user_subscriptions)}\n"
        f"Есть активная подписка: {'Да' if is_active else 'Нет'}"
    )
    return res


def format_user_subscriptions_history(user_subscriptions: list[Subscription]) -> str:
    res = "Подписки:\n"
    for i, user_subscription in enumerate(user_subscriptions):
        res += f"{i}) {user_subscription.plan} - {user_subscription.start_date} - {user_subscription.end_date}\n"
    return res
