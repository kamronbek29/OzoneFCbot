# coding=utf-8
from admin.admin_cmd_func import get_users_count_func, send_everyone_func, get_deleted_count, publish_exercise


async def admin(message):
    if message.text == '/get_users_count':
        await get_users_count_func(message)

    elif message.text == '/send_everyone':
        await send_everyone_func()

    elif message.text == '/get_deleted_count':
        await get_deleted_count(message)

    elif message.text == '/publish_exercise':
        await publish_exercise(message)



