# coding=utf-8
import json
import locale
import calendar

from datetime import datetime, timedelta
from operator import itemgetter

from aiogram.utils import executor
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from buttons import user_buttons, reject_button
from main import dp, user_info, Username, ADMIN_LIST_COMMANDS, competition_db, Results, GetResult, GetVideo
from config import admin_id

from admin_pac.admin import admin_func
from message_strings import message_stings
from important_functions import send_msg, on_startup, save_user_result, send_video_functions

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


########################################################################################################################


# Команды для Админа
@dp.message_handler(lambda message: message.from_user.id in [int(admin_id), 653391824], commands=ADMIN_LIST_COMMANDS)
async def admin_commands(message: Message):
    if message.text == '/admin':
        await send_msg(message.chat.id, 'admin_string')
        return
    await admin_func(message)


########################################################################################################################

# Ответ на команду /start
@dp.message_handler(commands=['start'])
async def start_command(message: Message):
    is_user_exist = user_info.get(message.from_user.id)
    if not is_user_exist:
        await send_msg(message.chat.id, message_stings['first_start_message'], format_msg=message.from_user.full_name)
        await Username.ask_username.set()
    else:
        user_name = str(user_info.get(message.from_user.id), 'utf-8')
        await send_msg(message.chat.id, message_stings['start_message'], format_msg=user_name, markup=user_buttons)


# Запуск определенной функции для каждой Соц Сети
@dp.message_handler(state=Username.ask_username)
async def ask_user_name_state(message: Message, state: FSMContext):
    if message.text == '/start':
        await send_msg(message.chat.id, message_stings['rejected'], markup=user_buttons)
        await state.finish()

    elif ' ' not in message.text:
        await send_msg(message.chat.id, message_stings['wrong_name'])
        await Username.ask_username.set()

    else:
        user_info.set(message.from_user.id, message.text)
        await send_msg(message.chat.id, message_stings['name_saved'], format_msg=message.text, markup=user_buttons)
        await state.finish()


########################################################################################################################


@dp.message_handler(lambda message: message.text in ['Получить упражения', '/get_exercise'])
async def get_exercise_command(message: Message):
    my_date = datetime.today()
    a = calendar.day_name[my_date.weekday()]

    if a == 'воскресенье':
        await send_msg(message.chat.id, 'Сегодня воскресенье, отдохните сами и дайте отдохунть другим)')
        return

    date_today = datetime.today().strftime('%d-%B')
    today_datetime = datetime.today()
    one_day = timedelta(days=1)
    tomorrow_date = (today_datetime + one_day).strftime('%d-%B')
    yesterday_date = (today_datetime - one_day).strftime('%d-%B')

    list_of_exercises = competition_db.get(f'{date_today}:{tomorrow_date}')
    if list_of_exercises is None:
        list_of_exercises = competition_db.get(f'{yesterday_date}:{date_today}')

    if list_of_exercises is None:
        await send_msg(message.chat.id, message_stings['no_exercise'],
                       format_msg=date_today, markup=user_buttons)
    else:
        make_json_obj = json.loads(list_of_exercises)
        list_of_exercises_str = make_json_obj['today_exercise']
        format_msg = f'{date_today}\n\n{list_of_exercises_str}'
        await send_msg(message.chat.id, message_stings['send_exercise'], format_msg=format_msg, markup=user_buttons)


########################################################################################################################


@dp.message_handler(lambda message: message.text in ['Участники соревнования', '/all_competitors'])
async def all_competitors_command(message: Message, state: FSMContext):
    my_date = datetime.today()
    a = calendar.day_name[my_date.weekday()]

    if a == 'воскресенье':
        await send_msg(message.chat.id, 'Сегодня воскресенье, отдохните сами и дайте отдохунть другим)')
        return

    date_today = datetime.today().strftime('%d-%B')
    today_datetime = datetime.today()
    one_day = timedelta(days=1)
    tomorrow_date = (today_datetime + one_day).strftime('%d-%B')
    yesterday_date = (today_datetime - one_day).strftime('%d-%B')

    all_competitors = competition_db.get(f'{date_today}:{tomorrow_date}')
    if all_competitors is None:
        all_competitors = competition_db.get(f'{yesterday_date}:{date_today}')

    if all_competitors is not None:
        json_object = json.loads(all_competitors)
        list_of_users_info = json_object['competitors']

        if list_of_users_info is None:
            await send_msg(message.chat.id, message_stings['no_competitors'], markup=user_buttons)
            return
        else:
            str_of_users_info = str(list_of_users_info).split('!!!')

            new_users_info = []
            for one_user_info in str_of_users_info:
                one_user_info_js = json.loads(one_user_info.replace("'", '"'))
                user_name = one_user_info_js['user_name']

                user_time = one_user_info_js['user_time']
                time_in_seconds = float(str(user_time).split(':')[0]) * 60 + float(str(user_time).split(':')[1])

                video_id = one_user_info_js['user_video_id']
                user_video_url = one_user_info_js['user_video_url']

                user_result = {
                    "user_name": user_name,
                    "user_time": int(time_in_seconds),
                    "user_video_id": video_id,
                    "user_video_url": user_video_url
                }
                new_users_info.append(user_result)
            sorted_user_infos = sorted(new_users_info, key=itemgetter('user_time'), reverse=False)

            list_of_user_result = []
            buttons = []

            result_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            button_reject = KeyboardButton('Отменить ⛔️')
            result_markup.add(button_reject)

            for i, sorted_user_info in enumerate(sorted_user_infos, start=1):
                user_info_json = json.loads(str(sorted_user_info).replace("'", '"'))

                user_name = user_info_json['user_name']
                user_time = user_info_json['user_time']

                minutes = int((float(user_time) / 60))
                seconds = int(float(user_time)) % 60

                if seconds < 10:
                    seconds = f'0{seconds}'

                result_time_minutes = f'{minutes}:{seconds}'

                if user_info_json['user_video_url'] == 'No video':
                    video_url = 'Видео нет!'
                else:
                    video_url = '[Ссылка на видео]({})'.format(user_info_json['user_video_url'])
                    result_button = KeyboardButton(f'Видео {i}ого участника')
                    buttons.append(f'Видео {i}ого участника')
                    result_markup.add(result_button)

                user_result = f'{i}. {user_name} - {result_time_minutes} - {video_url}'
                list_of_user_result.append(user_result)

            await state.update_data(users_info=str_of_users_info)
            await state.update_data(buttons_info=buttons)

            list_of_user_result_str = '\n'.join(list_of_user_result)
            await send_msg(message.chat.id, list_of_user_result_str, markdown=True, markup=result_markup)
            await send_msg(message.chat.id, message_stings['if_not_reject'], markup=result_markup)
            await GetResult.get_result.set()

    else:
        await send_msg(message.chat.id, message_stings['no_exercise_to_compete'], markup=user_buttons,
                       format_msg=date_today)
        return


@dp.message_handler(state=GetResult.get_result)
async def send_result_command(message: Message, state: FSMContext):
    data = await state.get_data()
    users_info = data.get('users_info')
    buttons_info = data.get('buttons_info')

    if message.text == '/start' or message.text == 'Отменить ⛔️':
        await send_msg(message.chat.id, message_stings['rejected'], markup=user_buttons)
        await state.finish()
        return
    elif message.text in buttons_info:
        user_to_get = str(message.text).split('Видео ')[1].split('ого')[0]
        list_users_info = str(users_info[int(user_to_get) - 1]).replace("'", '"')
        user_video_result = json.loads(list_users_info)['user_video_id']
        if user_video_result == 'No video':
            await state.finish()
            return
        await send_video_functions(message.chat.id, str(user_video_result), message.text)
        await GetResult.get_result.set()
    else:
        await send_msg(message.chat.id, message_stings['choose_correct_action'])
        await GetResult.get_result.set()


########################################################################################################################


@dp.message_handler(lambda message: message.text in ['Опубликовать результат', '/send_result'])
async def send_result_command(message: Message):
    date_today = datetime.today().strftime('%d-%B')
    today_datetime = datetime.today()
    one_day = timedelta(days=1)
    tomorrow_date = (today_datetime + one_day).strftime('%d-%B')
    yesterday_date = (today_datetime - one_day).strftime('%d-%B')

    list_of_exercises = competition_db.get(f'{date_today}:{tomorrow_date}')
    if list_of_exercises is None:
        list_of_exercises = competition_db.get(f'{yesterday_date}:{date_today}')

    if list_of_exercises is None:
        await send_msg(message.chat.id, message_stings['no_exercise'], format_msg=date_today, markup=user_buttons)
        return

    make_json_obj = json.loads(list_of_exercises)
    list_of_exercises_str = make_json_obj['today_exercise']
    msg_to_send = message_stings['exercise_done'].format(date_today, list_of_exercises_str)

    await send_msg(message.chat.id, msg_to_send, markup=reject_button)
    await Results.ask_time.set()


# Запуск определенной функции для каждой Соц Сети
@dp.message_handler(state=Results.ask_time)
async def ask_time_state(message: Message, state: FSMContext):
    if message.text == 'Отменить ⛔️' or message.text == '/start':
        await send_msg(message.chat.id, message_stings['rejected'], markup=user_buttons)
        await state.finish()
        return

    if ':' not in message.text:
        await send_msg(message.chat.id, message_stings['wrong_time'])
    else:
        minutes = str(message.text).split(':')[0]
        seconds = str(message.text).split(':')[1]

        if len(seconds) == 1:
            time1 = f'{minutes}:{seconds}0'
            time2 = f'{minutes}:0{seconds}'
            time_button = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            time_button1 = KeyboardButton(time1)
            time_button2 = KeyboardButton(time2)
            time_button.add(time_button1).add(time_button2)

            choose_correct_time = message_stings['correct_time'].format(time1, time2)
            await send_msg(message.chat.id, choose_correct_time, markup=time_button)
            await Results.ask_time.set()
            return

        elif float(seconds) > 59:
            plus_minutes = int((float(seconds) / 60))

            minutes = int(float(minutes)) + plus_minutes
            seconds = int(float(seconds)) % 60

            if seconds < 10:
                seconds = f'0{seconds}'

            user_time_result = f'{minutes}:{seconds}'

            msg_to_send = message_stings['send_video'].format(user_time_result, user_time_result)
            await send_msg(message.chat.id, msg_to_send, markup=reject_button)

            await state.update_data(user_time=message.text)
            await Results.ask_video.set()

        elif minutes.isdigit() and seconds.isdigit():
            msg_to_send = message_stings['send_video'].format(message.text, message.text)
            await send_msg(message.chat.id, msg_to_send, markup=reject_button)

            await state.update_data(user_time=message.text)
            await Results.ask_video.set()

        else:
            await send_msg(message.chat.id, message_stings['time_latter'],
                           format_msg=message.text, markup=reject_button)
            await Results.ask_time.set()


@dp.message_handler(state=Results.ask_video, content_types=['video', 'text'])
async def ask_video_state(message: Message, state: FSMContext):
    if message.text == 'Отменить ⛔️' or message.text == '/start':
        await send_msg(message.chat.id, message_stings['rejected'], markup=user_buttons)
        await state.finish()
        return

    elif message.video:
        data = await state.get_data()
        user_time = data.get('user_time')
        user_sent_video_duration = message.video.duration
        time_in_seconds = float(str(user_time).split(':')[0]) * 60 + float(str(user_time).split(':')[1])

        if time_in_seconds > user_sent_video_duration:
            minutes = int((float(user_sent_video_duration) / 60))
            seconds = int(float(user_sent_video_duration)) % 60

            video_time = f'{minutes}:{seconds}'
            msg_to_send = message_stings['incorrect_video'].format(user_time, video_time)
            await send_msg(message.chat.id, msg_to_send, markup=reject_button)
            await Results.ask_video.set()
            return

        else:
            video_file_url = await message.video.get_url()
            await save_user_result(message.from_user.id, user_time, message.video.file_id, video_file_url)

        video_file_url = await message.video.get_url()
        msg_to_send = message_stings['results_successfully_saved'].format(user_time, video_file_url)
        await send_msg(message.chat.id, msg_to_send, markdown=True, markup=user_buttons)
        await state.finish()

    else:
        if message.text == '/later':
            data = await state.get_data()
            user_time = data.get('user_time')
            await save_user_result(message.from_user.id, user_time, None, None)
            await send_msg(message.chat.id, 'later', format_msg=user_time, markup=user_buttons)
            await state.finish()
        else:
            await send_msg(message.chat.id, 'choose_correct_action')
            await Results.ask_video.set()
            return


########################################################################################################################


@dp.message_handler(lambda message: message.text in ['Отправить видео', '/send_video'])
async def all_competitors_command(message: Message, state: FSMContext):
    my_date = datetime.today()
    a = calendar.day_name[my_date.weekday()]

    if a == 'воскресенье':
        await send_msg(message.chat.id, 'Сегодня воскресенье, отдохните сами и дайте отдохунть другим)')
        return

    date_today = datetime.today().strftime('%d-%B')
    today_datetime = datetime.today()
    one_day = timedelta(days=1)
    tomorrow_date = (today_datetime + one_day).strftime('%d-%B')
    yesterday_date = (today_datetime - one_day).strftime('%d-%B')

    all_competitors = competition_db.get(f'{date_today}:{tomorrow_date}')
    if all_competitors is None:
        all_competitors = competition_db.get(f'{yesterday_date}:{date_today}')

    username = str(user_info.get(message.from_user.id), 'utf-8')

    if all_competitors is not None:
        json_object = json.loads(all_competitors)
        list_of_users_info = json_object['competitors']

        if list_of_users_info is None:
            await send_msg(message.chat.id, message_stings['no_competitors'], markup=user_buttons)
            return
        else:
            str_of_users_info = str(list_of_users_info).split('!!!')
            for user_result_info in str_of_users_info:
                user_result_info = user_result_info.replace("'", '"')
                user_info_result = json.loads(user_result_info)

                if user_info_result['user_name'] == username:
                    user_time = user_info_result['user_time']

                    if user_info_result['user_video_id'] == 'No video':
                        message_to_send = message_stings['send_video_state'].format(user_time, user_time)
                        await send_msg(message.chat.id, message_to_send, markup=reject_button)

                        await state.update_data(user_time=user_time)
                        await state.update_data(list_of_users_info=list_of_users_info)
                        await GetVideo.get_video.set()
                        return

            await send_msg(message.chat.id, 'Похоже, что у вас нету результатов без видео', markup=user_buttons)
            await state.finish()
    else:
        await send_msg(message.chat.id, message_stings['no_exercise'], format_msg=date_today, markup=user_buttons)
        return


@dp.message_handler(state=GetVideo.get_video, content_types=['video', 'text'])
async def send_result_command(message: Message, state: FSMContext):
    if message.text == '/start' or message.text == 'Отменить ⛔️':
        await send_msg(message.chat.id, message_stings['rejected'], markup=user_buttons)
        await state.finish()
        return

    elif message.video:
        data = await state.get_data()
        user_time = data.get('user_time')
        list_of_users_info = data.get('list_of_users_info')

        user_sent_video_duration = message.video.duration
        time_in_seconds = float(str(user_time).split(':')[0]) * 60 + float(str(user_time).split(':')[1])

        if time_in_seconds > user_sent_video_duration:
            minutes = int((float(user_sent_video_duration) / 60))
            seconds = int(float(user_sent_video_duration)) % 60

            video_time = f'{minutes}:{seconds}'
            msg_to_send = message_stings['incorrect_video'].format(user_time, video_time)
            await send_msg(message.chat.id, msg_to_send, markup=reject_button)
            await Results.ask_video.set()
            return

        else:
            str_of_users_info = str(list_of_users_info).split('!!!')
            for user_result in str_of_users_info:
                if user_time in user_result:
                    str_of_users_info.pop(str_of_users_info.index(user_result))

            video_file_url = await message.video.get_url()
            await save_user_result(message.from_user.id, user_time, message.video.file_id, video_file_url,
                                   competitors_list=str_of_users_info)

        video_file_url = await message.video.get_url()
        msg_to_send = message_stings['results_successfully_saved'].format(user_time, video_file_url)
        await send_msg(message.chat.id, msg_to_send, markdown=True, markup=user_buttons)
        await state.finish()
    else:
        await send_msg(message.chat.id, message_stings['choose_correct_action'])
        await GetVideo.get_video.set()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
