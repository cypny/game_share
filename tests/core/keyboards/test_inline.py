import pytest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Исправляем импорт - напрямую из файла inline.py
from game_share_bot.core.keyboards.inline import (
    main_menu_kb,
    personal_cabinet_kb,
    return_kb,
    admin_kb,
    confirmation_kb
)


class TestInlineKeyboards:
    def test_main_menu_kb_structure(self):
        keyboard = main_menu_kb()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3

        catalog_button = keyboard.inline_keyboard[0][0]
        assert catalog_button.text == "🎮 Каталог"

        personal_button = keyboard.inline_keyboard[1][0]
        assert personal_button.text == "👤 Личный кабинет"

        help_button = keyboard.inline_keyboard[2][0]
        assert help_button.text == "🆘 Поддержка"

    def test_personal_cabinet_kb_structure(self):
        keyboard = personal_cabinet_kb()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 4

        rented_button = keyboard.inline_keyboard[0][0]
        assert rented_button.text == "🎮 Арендованные диски"

        subscription_button = keyboard.inline_keyboard[1][0]
        assert subscription_button.text == "📦 Управление подпиской"

        queue_button = keyboard.inline_keyboard[2][0]
        assert queue_button.text == "📋 Моя очередь"

        back_button = keyboard.inline_keyboard[3][0]
        assert back_button.text == "⬅️ Назад"

    def test_return_kb_structure(self):
        from game_share_bot.core.callbacks.menu import MenuCallback
        callback_data = MenuCallback(section='main')
        keyboard = return_kb(callback_data)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1

        back_button = keyboard.inline_keyboard[0][0]
        assert back_button.text == "⬅️ Назад"

    def test_admin_kb_structure(self):
        keyboard = admin_kb()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2
        assert len(keyboard.inline_keyboard[0]) == 2
        assert len(keyboard.inline_keyboard[1]) == 1

    def test_confirmation_kb_structure(self):
        keyboard = confirmation_kb()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2

        confirm_button = keyboard.inline_keyboard[0][0]
        assert confirm_button.text == "✅ Подтвердить"

        cancel_button = keyboard.inline_keyboard[1][0]
        assert cancel_button.text == "❌ Отмена"