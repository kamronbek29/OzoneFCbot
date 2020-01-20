# coding=utf-8
import calendar
import time
import locale
from datetime import datetime, timedelta

from buttons import admin_sure_button, reject_button
from message_strings import message_stings
from main import dp, user_info, Exercise
from config import admin_id
from important_functions import send_msg, send_chat_act, delete_waiting_message, save_json
from admin_pac.send_everyone import check_admin_command
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


async def get_users_count_func(message):
    count = len(user_info.keys())
    msg = 'Всего {} пользователей, которые используют этот бот'.format(count)
    await send_msg(message.chat.id, msg)


async def send_everyone_func():
    await check_admin_command()


async def get_deleted_count(message):
    waiting_message = await send_msg(admin_id, 'message_wait')
    delete_number = 0
    success_number = 0

    users_id = user_info.keys()
    count = len(users_id)
    deleted_users = []
    for i, user_id in enumerate(users_id):
        if i % 10 != 0:
            pass
        else:
            time.sleep(1)

        try:
            await send_chat_act(int(user_id))
            success_number += 1
        except:
            deleted_user_name = str(user_info.get(user_id), 'utf-8')
            deleted_users.append(deleted_user_name)
            delete_number += 1

    list_deleted_user_name = 'Нет'
    if deleted_users:
        list_deleted_user_name = '\n'.join(deleted_users)

    await send_msg(admin_id, f'Все еще используют вашего бота: {success_number}\n'
                             f'Удалили вашего бота: {delete_number}\n'
                             f'Всего нажали на start: {count}\n'
                             f'Имена тех, кто удалил: {list_deleted_user_name}')

    await delete_waiting_message(message, waiting_message)


async def publish_exercise(message):
    my_date = datetime.today()
    a = calendar.day_name[my_date.weekday()]

    if a == 'воскресенье':
        await send_msg(message.chat.id, 'Сегодня воскресенье, отдохните сами и дайте отдохунть другим)')
        return

    today_date = datetime.today().strftime('%d-%B')
    await send_msg(message.chat.id, message_stings['ask_exercise'], format_msg=today_date, markup=reject_button)
    await Exercise.ask_exercise.set()


@dp.message_handler(state=Exercise.ask_exercise)
async def publish_exercise_state(message: Message, state: FSMContext):
    if message.text == 'Отменить ⛔️':
        await send_msg(message.chat.id, message_stings['rejected'])
        await state.finish()
        return

    await state.update_data(exercise_for_today=message.text)

    today_date = datetime.today().strftime('%d-%B')
    today_datetime = datetime.today()
    date_tomorrow = timedelta(days=1)
    tomorrow_date = (today_datetime + date_tomorrow).strftime('%d-%B')

    msg_to_send = message_stings['sure_to_publish'].format(f'{today_date} и на {tomorrow_date}', message.text)
    await send_msg(message.chat.id, msg_to_send, markup=admin_sure_button)
    await Exercise.sure_to_publish.set()


@dp.message_handler(state=Exercise.sure_to_publish)
async def publish_exercise_state(message: Message, state: FSMContext):
    data = await state.get_data()
    exercise_for_today = data.get('exercise_for_today')
    if message.text == 'Да':
        err, is_saved = await save_json(exercise_for_today, to_publish=True)

        if err is None and is_saved:
            await send_msg(message.chat.id, message_stings['successfully_saved'])
        else:
            format_msg = f'{err} в admin/admin_cmd_func/publish_exercise_state'
            await send_msg(message.chat.id, message_stings['something_wrong'], format_msg=format_msg)

        await state.finish()
        return

    elif message.text == 'Нет':
        await send_msg(message.chat.id, message_stings['rejected'])
        await state.finish()
        return
    else:
        await send_msg(message.chat.id, message_stings['choose_correct_action'], markup=admin_sure_button)
        await Exercise.sure_to_publish.set()
        return



