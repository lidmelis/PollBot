from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


choose_options_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Произвольный ответ", callback_data="arbitrary_choice")
        ],
        [   
            InlineKeyboardButton(text="Одиночный ответ", callback_data="single_choice")
        ],
        [   
            InlineKeyboardButton(text="Множественный ответ",callback_data="multipy_choice")
        ]
    ]
)


end_keyboard = InlineKeyboardMarkup(
    inline_keyboard = [
        [
            InlineKeyboardButton(text="Закончить опрос", callback_data="end_poll")
        ]
    ]
)
