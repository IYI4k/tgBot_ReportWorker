from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/send")],
    {KeyboardButton(text="/start")}
],
    resize_keyboard=True,
    input_field_placeholder='Нажми что-нибудь'
)