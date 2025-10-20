import pytest
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from game_share_bot.core.keyboards.reply import register_kb


class TestReplyKeyboards:
    def test_register_kb_structure(self):
        keyboard = register_kb()

        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert keyboard.resize_keyboard is True
        assert keyboard.one_time_keyboard is True

        assert len(keyboard.keyboard) == 1
        assert len(keyboard.keyboard[0]) == 1

        button = keyboard.keyboard[0][0]
        assert isinstance(button, KeyboardButton)
        assert button.text == "Отправить номер"
        assert button.request_contact is True