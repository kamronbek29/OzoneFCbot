# coding=utf-8
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message

from message_strings import message_stings
from main import dp, Admin, user_info
from buttons import ask_to_send_buttons, reject_button, admin_sure_button
from config import admin_id
from important_functions import send_msg


# Спросить кому отправить
async def check_admin_command():
    await send_msg(admin_id, message_stings['ask_to_send'], markup=ask_to_send_buttons)
    await Admin.ask_to_send.set()


# Спросить что отправить или каким пользователям отправить
@dp.message_handler(state=Admin.ask_to_send)
async def ask_admin_to_send(message: Message, state: FSMContext):
    if message.text == 'Отправить всем':
        await send_msg(message.chat.id, message_stings['what_to_send_everyone'], markup=reject_button)

    elif message.text == 'Отправить нескольким':
        users_id = user_info.keys()

        users_info_list = []
        for i, user_id in enumerate(users_id, start=1):
            user_name = str(user_info.get(user_id), 'utf-8')
            user_id = str(user_id, 'utf-8')

            users_id_and_name = f'{i}. {user_id} - {user_name}'
            users_info_list.append(users_id_and_name)

        user_info_str = '\n'.join(users_info_list)

        await send_msg(message.chat.id, message_stings['list_users'], format_msg=user_info_str)
        await send_msg(message.chat.id, message_stings['ask_users_id'], markup=reject_button)

    elif message.text == 'Отменить ⛔️':
        await send_msg(message.chat.id, message_stings['rejected'])
        await state.finish()
        return

    else:
        await send_msg(message.chat.id, message_stings['choose_correct_action'], markup=ask_to_send_buttons)
        await Admin.ask_to_send.set()
        return

    await state.update_data(user_message=message.text)
    await Admin.ask.set()


# Спросить, уверен ли админ в отправке сообщение всем пользователям
@dp.message_handler(state=Admin.ask)
async def ask_admin(message: Message, state: FSMContext):
    data = await state.get_data()
    user_state = data.get('user_message')

    if user_state == 'Отправить всем':
        if message.text == 'Отменить ⛔️':
            await send_msg(message.chat.id, message_stings['rejected'])
            await state.finish()
            return

        await state.update_data(message_to_send=message.text)
        await send_msg(admin_id, message_stings['is_admin_sure'], format_msg=message.text, markup=admin_sure_button)
        await Admin.sure.set()

    elif user_state == 'Отправить нескольким':
        if message.text == 'Отменить ⛔️':
            await send_msg(message.chat.id, message_stings['rejected'])
            await state.finish()
            return

        list_of_users_id = str(message.text).split(', ')
        await state.update_data(list_of_users_id=list_of_users_id)

        list_user_names = []
        for user_id in list_of_users_id:
            if user_info.get(user_id) is None:
                await send_msg(message.chat.id, message_stings['no_user'], format_msg=user_id)
                continue
            user_name = str(user_info.get(user_id), 'utf-8')
            list_user_names.append(user_name)

        if not list_user_names:
            await send_msg(message.chat.id, message_stings['no_sent_users'], format_msg=message.text)
            await state.finish()
            return

        user_names_str = '\n'.join(list_user_names)
        await send_msg(message.chat.id, message_stings['what_to_send_some'],
                       format_msg=user_names_str, markup=reject_button)

        await Admin.what_send_some.set()

    elif message.text == 'Отменить ⛔️':
        await send_msg(message.chat.id, message_stings['rejected'])
        await state.finish()


@dp.message_handler(state=Admin.what_send_some)
async def ask_what_send_some(message: Message, state: FSMContext):
    if message.text == 'Отменить ⛔️':
        await send_msg(message.chat.id, message_stings['rejected'])
        await state.finish()
        return

    await state.update_data(message_to_send=message.text)
    await send_msg(admin_id, message_stings['is_admin_sure'], format_msg=message.text, markup=admin_sure_button)
    await Admin.sure.set()


@dp.message_handler(state=Admin.sure)
async def sure(message: Message, state: FSMContext):
    confidence = message.text
    data = await state.get_data()
    message_to_send = data.get('message_to_send')
    user_state = data.get('user_message')

    if confidence == 'Да':
        if user_state == 'Отправить всем':
            users_id = user_info.keys()
        elif user_state == 'Отправить нескольким':
            users_id = data.get('list_of_users_id')
        else:
            return

        delete_number = 0
        success_number = 0
        for user_id in users_id:
            try:
                await send_msg(int(user_id), message_to_send)
                success_number += 1
            except:
                delete_number += 1
                user_name = user_info.get(user_id)
                msg = 'Этот пользователь возможно удалил вашего бота {}'.format(user_name)
                await send_msg(admin_id, msg)

        count = delete_number + success_number
        await send_msg(message.chat.id, f'Ваше сообщение было отправлено всем пользователям\n'
                                        f'Всего отправлено {count}\n'
                                        f'Успешно отправлено: {success_number}\n'
                                        f'Удалили бота: {delete_number}\n')

        await state.finish()

    elif confidence == 'Нет':
        await send_msg(message.chat.id, message_stings['rejected'])
        await state.finish()

    else:
        await send_msg(message.chat.id, 'Вы отменили действия')
        await Admin.what_send_some.set()


