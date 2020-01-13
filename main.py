import asyncio
import redis
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN
from aiogram.dispatcher.filters.state import StatesGroup, State


loop = asyncio.get_event_loop()
bot = Bot(BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)

user_info = redis.StrictRedis(host='localhost', port=6379, db=4)
competition_db = redis.StrictRedis(host='localhost', port=6379, db=5)


class Username(StatesGroup):
    ask_username = State()


class Admin(StatesGroup):
    ask_to_send = State()
    ask = State()
    ask_some_send = State()
    what_send_some = State()
    sure = State()


class Exercise(StatesGroup):
    ask_exercise = State()
    sure_to_publish = State()


class Results(StatesGroup):
    ask_time = State()
    ask_video = State()
    sure_to_publish = State()


class GetResult(StatesGroup):
    get_result = State()


class GetVideo(StatesGroup):
    get_video = State()


ADMIN_LIST_COMMANDS = ['get_users_count', 'send_everyone', 'admin', 'get_deleted_count', 'publish_exercise']
