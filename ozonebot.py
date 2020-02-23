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
        msg = '[{0}](tg://user?id={1}) начал использовать бот \nUser ID: {2}' \
              .format(message.from_user.full_name, message.from_user.id, message.from_user.id)

        await send_msg('-1001197338062', msg, markdown=True, channel=True)
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

        msg = 'Пользователя [{0}](tg://user?id={1}) зовут {2}' \
            .format(message.from_user.full_name, message.from_user.id, message.text)

        await send_msg('-1001197338062', msg, markdown=True, channel=True)

        await state.finish()


########################################################################################################################


@dp.message_handler(lambda message: message.text in ['Получить упражения', '/get_exercise'])
async def get_exercise_command(message: Message):
    my_date = datetime.today().weekday()

    if int(my_date) == 6:
        await send_msg(message.chat.id, 'Сегодня воскресенье, отдохните сами и дайте отдохунть другим)')
        return

    list_of_exercises = competition_db.get('today exercise')

    if list_of_exercises is None:
        await send_msg(message.chat.id, message_stings['no_exercise'], markup=user_buttons)
    else:
        make_json_obj = json.loads(list_of_exercises)
        list_of_exercises_str = make_json_obj['today_exercise']
        await send_msg(message.chat.id, message_stings['send_exercise'], format_msg=list_of_exercises_str, markup=user_buttons)


########################################################################################################################


@dp.message_handler(lambda message: message.text in ['Участники соревнования', '/all_competitors'])
async def all_competitors_command(message: Message, state: FSMContext):
    my_date = datetime.today().weekday()

    if int(my_date) == 6:
        await send_msg(message.chat.id, 'Сегодня воскресенье, отдохните сами и дайте отдохунть другим)')
        return

    all_competitors = competition_db.get('today exercise')
    if all_competitors is not None:
        json_object = json.loads(all_competitors)
        list_of_users_info = json_object['competitors']

        if list_of_users_info is None:
            await send_msg(message.chat.id, message_stings['no_competitors'], markup=user_buttons)
            return
        else:
            str_of_users_info = str(list_of_users_info).split('!!!')
            print(str_of_users_info)

            new_users_info = []
            for one_user_info in str_of_users_info:
                one_user_info_js = json.loads(one_user_info.replace("'", '"'))
                user_name = one_user_info_js['user_name']

                user_time = one_user_info_js['user_time']
                time_in_seconds = float(str(user_time).split(':')[0]) * 60 + float(str(user_time).split(':')[1])

                user_result = {
                    "user_name": user_name,
                    "user_time": int(time_in_seconds),
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

                user_result = f'{i}. {user_name} - {result_time_minutes}'
                list_of_user_result.append(user_result)

            await state.update_data(users_info=str_of_users_info)
            await state.update_data(buttons_info=buttons)

            list_of_user_result_str = '\n'.join(list_of_user_result)
            await send_msg(message.chat.id, list_of_user_result_str, markdown=True, markup=result_markup)
            await send_msg(message.chat.id, message_stings['if_not_reject'], markup=result_markup)
            await GetResult.get_result.set()

    else:
        await send_msg(message.chat.id, message_stings['no_exercise_to_compete'], markup=user_buttons)
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
    my_date = datetime.today().weekday()

    if int(my_date) == 6:
        await send_msg(message.chat.id, 'Сегодня воскресенье, отдохните сами и дайте отдохунть другим)')
        return

    list_of_exercises = competition_db.get('today exercise')
    if list_of_exercises is None:
        await send_msg(message.chat.id, message_stings['no_exercise'], markup=user_buttons)
        return

    make_json_obj = json.loads(list_of_exercises)
    list_of_exercises_str = make_json_obj['today_exercise']
    msg_to_send = message_stings['exercise_done'].format(list_of_exercises_str)

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
            await save_user_result(message.from_user.id, user_time_result)
            await send_msg(message.chat.id, 'results_successfully_saved', format_msg=user_time_result)
            await state.finish()

        elif minutes.isdigit() and seconds.isdigit():
            user_time_result = f'{minutes}:{seconds}'
            await save_user_result(message.from_user.id, user_time_result)
            await send_msg(message.chat.id, 'results_successfully_saved', format_msg=user_time_result)
            await state.finish()

        else:
            await send_msg(message.chat.id, message_stings['time_latter'],
                           format_msg=message.text, markup=reject_button)
            await Results.ask_time.set()


########################################################################################################################


@dp.message_handler(lambda message: message.text in ['Отправить видео', '/send_video'])
async def all_competitors_command(message: Message, state: FSMContext):
    my_date = datetime.today().weekday()

    if int(my_date) == 6:
        await send_msg(message.chat.id, 'Сегодня воскресенье, отдохните сами и дайте отдохунть другим)')
        return

    list_of_exercises = competition_db.get('today exercise')
    if list_of_exercises is None:
        await send_msg(message.chat.id, message_stings['no_exercise'], markup=user_buttons)
        return

    await send_msg(message.chat.id, 'send_video', markup=reject_button)
    await GetVideo.get_video.set()


@dp.message_handler(state=GetVideo.get_video, content_types=['video', 'text'])
async def send_result_command(message: Message, state: FSMContext):
    if message.text == '/start' or message.text == 'Отменить ⛔️':
        await send_msg(message.chat.id, message_stings['rejected'], markup=user_buttons)
        await state.finish()
        return

    elif message.video:
        video_id = message.video.file_id
        print(video_id)
        expire_time = competition_db.ttl('today exercise')
        all_videos = competition_db.get('all videos')
        if all_videos is None:
            competition_db.set('all videos', video_id, ex=expire_time)
        else:
            all_videos_id_list = str(all_videos, 'utf-8').split(', ')
            all_videos_id_list.append(video_id)
            all_videos_str = ', '.join(all_videos_id_list)
            competition_db.set('all videos', all_videos_str, ex=expire_time)

        await state.finish()
        await send_msg(message.chat.id, 'video_saved')
    else:
        await send_msg(message.chat.id, message_stings['choose_correct_action'])
        await GetVideo.get_video.set()


@dp.message_handler(lambda message: message.text in ['Опубликованные видео', '/get_videos'])
async def get_all_videos(message: Message):
    my_date = datetime.today().weekday()

    if int(my_date) == 6:
        await send_msg(message.chat.id, 'Сегодня воскресенье, отдохните сами и дайте отдохунть другим)')
        return

    all_videos = competition_db.get('all videos')
    if all_videos is None:
        await send_msg(message.chat.id, 'no_video_yet')
    else:
        all_videos_ids = str(all_videos, 'utf-8').split(', ')
        for video_id in all_videos_ids:
            await send_video_functions(message.chat.id, video_id)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
