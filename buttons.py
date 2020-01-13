# coding=utf-8
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


ask_to_send_buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
ask_to_send_btn1 = KeyboardButton('Отправить всем')
ask_to_send_btn2 = KeyboardButton('Отправить нескольким')
ask_to_send_btn3 = KeyboardButton('Отменить ⛔️')
all_ask_to_send_buttons = ask_to_send_btn1, ask_to_send_btn2, ask_to_send_btn3
ask_to_send_buttons.add(*all_ask_to_send_buttons)


reject_button = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
reject_button1 = KeyboardButton('Отменить ⛔️')
reject_button.add(reject_button1)


admin_sure_button = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
admin_sure_button1 = KeyboardButton('Да')
admin_sure_button2 = KeyboardButton('Нет')
all_admin_sure_buttons = admin_sure_button1, admin_sure_button2
admin_sure_button.add(*all_admin_sure_buttons)


user_buttons = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
user_button1 = KeyboardButton('Участники соревнования')
user_button2 = KeyboardButton('Получить упражения')
user_button3 = KeyboardButton('Опубликовать результат')
user_button4 = KeyboardButton('Отправить видео')
all_user_buttons = user_button1, user_button2, user_button3, user_button4
user_buttons.add(*all_user_buttons)
