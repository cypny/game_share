from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from game_share_bot.core.callbacks import MenuCallback
from game_share_bot.core.handlers.utils import respond_user
from game_share_bot.core.keyboards import main_menu_kb
from game_share_bot.core.keyboards.inline import return_kb
from game_share_bot.domain.enums import MenuSection
from game_share_bot.infrastructure.utils import get_logger

router = Router()
logger = get_logger(__name__)


@router.message(Command("menu"))
@router.callback_query(MenuCallback.filter_by_section(MenuSection.MAIN))
async def main_menu(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    text = "Главное меню"
    markup = main_menu_kb()
    await respond_user(event, text, markup)


@router.message(Command("help"))
@router.callback_query(F.data == "help")
async def handle_help(event: CallbackQuery | Message):
    text = "@cynpy_the_best"
    markup = return_kb(MenuCallback(section=MenuSection.MAIN))
    await respond_user(event, text, markup)
