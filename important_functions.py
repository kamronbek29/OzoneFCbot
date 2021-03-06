# coding=utf-8
import json
from datetime import datetime, timedelta
import locale

from aiogram.types.reply_keyboard import ReplyKeyboardRemove

from main import bot, competition_db, user_info
from config import admin_id
from message_strings import message_stings

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


# Send notification that bot started working
async def on_startup(*args):  # send errors to admin
    await bot.send_message(chat_id=admin_id, text="Бот запущен")


async def send_chat_act(user_id):
    await bot.send_chat_action(user_id, 'TYPING')


# Function to delete waiting message
async def delete_waiting_message(message, msg_to_delete):
    await bot.delete_message(message.chat.id, msg_to_delete.message_id)


# Function to send waiting message
async def send_msg(chat_id, msg_to_send, format_msg=False, markup=False, markdown=False, channel=False):
    if msg_to_send not in message_stings.keys():
        if format_msg is False:
            msg_to_send = msg_to_send
        else:
            msg_to_send = msg_to_send.format(format_msg)
    else:
        if format_msg is False:
            msg_to_send = message_stings[msg_to_send]
        else:
            msg_to_send = message_stings[msg_to_send].format(format_msg)

    if markup is False:
        if channel:
            markup = None
        else:
            markup = ReplyKeyboardRemove()

    if markdown:
        sent_message = await bot.send_message(chat_id, msg_to_send, reply_markup=markup, parse_mode='markdown',
                                              disable_web_page_preview=True)
    else:
        sent_message = await bot.send_message(chat_id, msg_to_send, reply_markup=markup,
                                              disable_web_page_preview=True)
    return sent_message


# Function to send a video
async def send_video_functions(chat_id, file_to_send, caption=None):
    try:
        await bot.send_video(chat_id, file_to_send, caption=caption)
    except Exception:
        await bot.send_animation(chat_id, file_to_send, caption=caption)


async def save_json(exercise=None, to_publish=None, competitors=None):
    try:
        if to_publish:
            json_object = {
                'today_exercise': str(exercise),
                'competitors': None
            }
            expire = 24 * 3600 * 6.5
            competition_db.set('today exercise', json.dumps(json_object), ex=int(expire))

        if competitors:
            json_object = {
                'today_exercise': str(exercise),
                'competitors': competitors
            }
            time_left = competition_db.ttl('today exercise')
            competition_db.set('today exercise', json.dumps(json_object), ex=time_left)

        return None, True
    except Exception as err:
        return err, False


async def save_user_result(user_id, user_time, competitors_list=None):
    json_object = competition_db.get('today exercise')
    if json_object is None:
        json_object = competition_db.get('today exercise')

    if json_object is not None:
        json_object = json.loads(json_object)

        today_exercise = json_object['today_exercise']
        competitors = json_object['competitors']

        user_result = {
            "user_name": str(user_info.get(user_id), 'utf-8'),
            "user_time": user_time,
        }

        if competitors_list is not None:
            competitors_list.append(json.dumps(user_result))
            competitors_str = '!!!'.join(competitors_list)
        else:
            if competitors is not None:
                competitors_list = str(competitors).split('!!!')
                competitors_list.append(json.dumps(user_result))
                competitors_str = '!!!'.join(competitors_list)
            else:
                competitors_str = user_result

        err, is_saved = await save_json(exercise=today_exercise, competitors=competitors_str)
        print(err, is_saved)


# asyncio.run(save_user_result('2312312123', '2:22', 'qDSDa'))
