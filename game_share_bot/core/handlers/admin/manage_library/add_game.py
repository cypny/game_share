from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.core.callbacks import AdminCallback, ConfirmationCallback
from game_share_bot.core.filters import IsAdmin
from game_share_bot.core.handlers.utils import (
    cancel_admin_action,
    get_game_adding_confirmation_text,
    get_list_of_categories_message,
    add_game,
)
from game_share_bot.core.keyboards import confirmation_kb
from game_share_bot.core.keyboards.inline.admin import add_game_image_kb, return_to_admin_manage_library_panel_kb
from game_share_bot.core.services.admin import try_parse_categories
from game_share_bot.core.states import AddGameState
from game_share_bot.domain.enums import AdminAction
from game_share_bot.infrastructure.repositories import GameRepository
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.callback_query(AdminCallback.filter_by_action(AdminAction.ADD_GAME), IsAdmin())
async def request_title(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Введите название игры:", reply_markup=return_to_admin_manage_library_panel_kb())
    await state.set_state(AddGameState.waiting_for_title)


@router.message(AddGameState.waiting_for_title, IsAdmin())
async def handle_title_and_request_category(message: Message, session: AsyncSession, state: FSMContext):
    await state.update_data({"title": message.text})
    await message.answer(
        "Укажите, к каким категориям относится игра\n\n"
        "Вы можете указать любое кол-во категорий для одной игры\n\n"
        "Доступные категории (вы также можете добавлять/удалять категории в отдельном меню):\n"
        f"{await get_list_of_categories_message(session)}\n\n"
        f"Введите категории через запятую без пробела, как написано сверху (регистр имеет значение!)\n"
        f"Например: RPG,Экшен,Приключения",
        reply_markup=return_to_admin_manage_library_panel_kb(),
    )
    await state.set_state(AddGameState.waiting_for_categories)


@router.message(AddGameState.waiting_for_categories, IsAdmin())
async def handle_categories_and_request_discs_count(message: Message, session: AsyncSession, state: FSMContext):
    categories = await try_parse_categories(message.text, session)
    if categories is None:
        await message.answer(
            "Некорректный ввод, возможно введенных категорий не существует",
            reply_markup=return_to_admin_manage_library_panel_kb(),
        )
    else:
        await state.update_data({"categories": categories})
        await message.answer(
            "Введите кол-во физических копий игры:\n\n"
            "(вы также сможете изменить этот параметр отдельно после добавления)",
            reply_markup=return_to_admin_manage_library_panel_kb(),
        )
        await state.set_state(AddGameState.waiting_for_discs_count)


@router.message(AddGameState.waiting_for_discs_count, IsAdmin())
async def handle_discs_count_and_request_description(message: Message, state: FSMContext):
    try:
        discs_count = int(message.text)
    except ValueError:
        await message.answer("Некорректный ввод - кол-во дисков должно быть числом!")
        return None

    await state.update_data({"discs_count": discs_count})
    await message.answer("Введите описание игры:", reply_markup=return_to_admin_manage_library_panel_kb())
    await state.set_state(AddGameState.waiting_for_description)
    return None


@router.message(AddGameState.waiting_for_description, IsAdmin())
async def handle_description_and_request_image(message: Message, state: FSMContext):
    await state.update_data({"description": message.text})
    await message.answer("Введите image url (опционально):", reply_markup=add_game_image_kb())
    await state.set_state(AddGameState.waiting_for_image)


@router.message(AddGameState.waiting_for_image, IsAdmin())
async def handle_image_and_request_confirmation(message: Message, state: FSMContext):
    await state.update_data({"image": message.text})
    data = await state.get_data()
    try:
        await message.answer_photo(
            photo=data["image"],
            caption=get_game_adding_confirmation_text(data),
            parse_mode=ParseMode.HTML,
            reply_markup=confirmation_kb(),
        )
    except TelegramBadRequest:
        await message.answer(
            "Что-то пошло не по плану(\n" "Проверьте корректность URL",
            reply_markup=return_to_admin_manage_library_panel_kb(),
        )
        await state.clear()
    else:
        await state.set_state(AddGameState.waiting_for_confirmation)


@router.callback_query(
    AddGameState.waiting_for_image, AdminCallback.filter_by_action(AdminAction.SKIP_IMAGE_INPUT), IsAdmin()
)
async def skip_image_and_request_confirmation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.answer()
    await callback.message.edit_text(
        get_game_adding_confirmation_text(data),
        parse_mode=ParseMode.HTML,
        reply_markup=confirmation_kb(),
    )
    await state.set_state(AddGameState.waiting_for_confirmation)


@router.callback_query(AddGameState.waiting_for_confirmation, ConfirmationCallback.filter_confirmed(), IsAdmin())
async def add_game_handler(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    result = await add_game(session, data)
    await callback.answer()
    await callback.message.delete()
    if result is None:
        await callback.message.answer("Не получилось добавить игру(\n" "Возможно, игра с таким названием уже добавлена")
    else:
        await callback.message.answer("Игра успешно добавлена")

    await state.clear()


@router.callback_query(AddGameState.waiting_for_confirmation, ConfirmationCallback.filter_canceled())
async def cancel_game_add(callback: CallbackQuery, state: FSMContext):
    await cancel_admin_action(callback, state)
