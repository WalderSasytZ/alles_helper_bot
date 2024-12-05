from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
from datetime import datetime

import database
import api_requests
import keyboards
from constants import texts

router = Router()


class BotState(StatesGroup):
    registration = State()
    find_user = State()
    add_user = State()
    set_role = State()
    delete_user = State()

    wait = State()

    menu_add_tags = State()
    menu_delete_tags = State()

    event_title = State()
    event_description = State()
    event_time = State()
    event_add_tags = State()


# Регистрация пользователя после /start
@router.message(BotState.registration)
async def registration(message, state):
    token = message.text.replace(' ', '')

    # Запрос на поиск незарегистрированного в боте юзера с нужным токеном, возвращает его website_id
    user_response = await api_requests.add_user(token, message.chat.id)

    if not user_response:
        await message.answer(texts['server_error'])
        return

    # Был ли токен уже активирован кем-то
    if user_response.status == 201:
        await message.answer(texts["activated_token"])
        return

    # Указан ли токен корректно и существует ли пользователь с таким токеном
    if user_response.status != 200:
        await message.answer(texts["incorrect_token"])
        return

    # Получаем имя и id на сайте
    website_id = (await user_response.json())['website_id']
    name_response = await api_requests.get_user_data(website_id)
    user_name = (await name_response.json())['first_name']

    await database.add_user(user_name, 0, message.chat.id, website_id)
    await message.answer(text=texts["welcome"][0] + user_name + texts["welcome"][1],
                         reply_markup=keyboards.main_menu_markup())
    await state.clear()


# Ввод названия события при его создании
@router.message(BotState.event_title)
async def insert_event_title(message, state):
    await state.update_data(event_title=message.text)
    await state.set_state(BotState.event_description)
    await message.answer(texts['enter_event_description'], reply_markup=keyboards.return_admin_markup())


# Ввод описания события при его создании
@router.message(BotState.event_description)
async def insert_event_title(message, state):
    await state.update_data(event_description=message.text)
    await state.set_state(BotState.event_time)
    await message.answer(texts['enter_event_time'], reply_markup=keyboards.return_admin_markup())


# Ввод даты события при его создании
@router.message(BotState.event_time)
async def insert_event_date(message, state):
    try:
        date = datetime.strptime(message.text, '%H:%M %d.%m.%y')
    except Exception:
        await message.answer(texts['invalid_date'])
        return

    await state.update_data(event_time=date)
    await message.answer(texts['enter_tags'], reply_markup=keyboards.return_admin_markup())
    await state.set_state(BotState.event_add_tags)


# Добавление тегов событию при его создании
@router.message(BotState.event_add_tags)
async def event_add_tags(message, state):
    entered_tags = message.text.replace(' ', '').lower().split(',')
    db_tags = [tag['name'] for tag in await database.get_tags_data()]

    new_tags = []
    existed_tags = []
    for tag in entered_tags:
        if len(tag):
            if tag in db_tags:
                existed_tags.append(tag)
            else:
                new_tags.append(tag)

    # Обрабатываем новые теги
    if len(new_tags) > 0:
        if await database.has_main_access(message.chat.id):
            await state.update_data(event_add_tags=(new_tags, entered_tags))
            await message.answer(texts['new_tags_main'] + ', '.join(new_tags), reply_markup=keyboards.confirm_add_tags_markup())
        elif await database.has_admin_access(message.chat.id):
            await message.answer(texts['new_tags_admin'][0] + ', '.join(new_tags) + texts['new_tags_admin'][1])
            await state.set_state(BotState.event_add_tags)
    else:
        data = await state.get_data()
        event_id = await database.add_general_event(data['event_title'], data['event_description'], data['event_time'])

        # Добавляем связи тегов и событий в БД
        for tag in entered_tags:
            await database.create_tag_event(event_id, tag)

        await message.answer(texts['event_created'], reply_markup=keyboards.return_admin_markup())
        await state.clear()


# Добавление тегов из меню админа
@router.message(BotState.menu_add_tags)
async def menu_add_tags(message, state):
    entered_tags = message.text.replace(' ', '').lower().split(',')
    db_tags = [tag['name'] for tag in await database.get_tags_data()]

    existed_tags = []
    for tag in entered_tags:
        if len(tag):
            if tag not in db_tags:
                await database.add_tag(tag)
            else:
                existed_tags.append(tag)

    await message.answer(texts['menu_tags_added'][0] + (len(existed_tags) > 0) *
                         (texts['menu_tags_added'][1] + ', '.join(existed_tags)),
                         reply_markup=keyboards.return_admin_markup())
    await state.clear()


# Удаление тегов из меню админа
@router.message(BotState.menu_delete_tags)
async def menu_delete_tags(message, state):
    entered_tags = message.text.replace(' ', '').lower().split(',')
    db_tags = [tag['name'] for tag in await database.get_tags_data()]

    unexisted_tags = []
    for tag in entered_tags:
        if tag in db_tags:
            await database.delete_tag(tag)
        else:
            unexisted_tags.append(tag)

    await message.answer(texts['menu_tags_deleted'][0] + (len(unexisted_tags) > 0) *
                         (texts['menu_tags_deleted'][1] + ', '.join(unexisted_tags)),
                         reply_markup=keyboards.return_admin_markup())
    await state.clear()


# Поиск пользователя
@router.message(BotState.find_user)
async def find_user(message, state):
    message_data = message.text
    tg_chat_id = message_data

    # Проверяем формат команды
    if '@' not in message_data and not message_data.isdigit():
        await message.answer(texts['invalid_format'])
        return

    # Если поиск по почте
    if '@' in message_data:
        response = await api_requests.get_user_by_mail(message_data)

        if not response:
            await message.answer(texts['server_error'])
            return

        if response.status == 404:
            await message.answer(texts['user_404'])
            return

        if response.status != 200:
            await message.answer(texts['server_error'])
            return

        tg_chat_id = (await response.json())['tg_chat_id']

        if not tg_chat_id or not await database.find_user(tg_chat_id):
            await message.answer(texts['user_not_in_bot'])
            return

    # Если поиск по id
    if message_data.isdigit() and not await database.find_user(tg_chat_id):
        await message.answer(texts['user_404'])
        return

    await message.answer(texts['user_found'], reply_markup=keyboards.found_user_markup())
    await state.update_data(find_user=tg_chat_id)


# Добавление пользователя
@router.message(BotState.add_user)
async def add_user(message, state):
    message_data = message.text.split()

    # Проверяем формат команды
    if len(message_data) < 3 or message_data[-2] not in ['0', '1', '2'] or not message_data[-1].isdigit():
        await message.answer(texts['invalid_format'])
        return

    # Проверяем наличие пользователя
    if await database.find_user(message_data[-1]):
        await message.answer(texts['already_added'])
        return

    # Добавляем в бд
    await database.add_user(' '.join(message_data[0:-2]), message_data[-2], message_data[-1])
    await message.answer(texts['user_added'], reply_markup=keyboards.return_admin_markup())
    await state.clear()


# Изменение роли существующего пользователя
@router.message(BotState.set_role)
async def set_role(message, state):
    tg_chat_id = (await state.get_data())['find_user']

    # Проверяем формат команды
    if message.text not in ['0', '1', '2']:
        await message.answer(texts['invalid_format'])
        return

    # Проверяем наличие пользователя
    if not await database.find_user(tg_chat_id):
        await message.answer(texts['user_404'])
        return

    # Добавляем в бд
    await database.set_role(message.text, tg_chat_id)
    await message.answer(texts['role_is_set'], reply_markup=keyboards.return_admin_markup())
    await state.clear()


# Удаление пользователя из БД
@router.message(BotState.delete_user)
async def delete_user(message, state):
    tg_chat_id = (await state.get_data())['find_user']

    # Проверяем наличие пользователя
    if not await database.find_user(tg_chat_id):
        await message.answer(texts['user_404'])
        return

    # Удаляем пользователя из бд
    await database.delete_user(tg_chat_id)
    await message.answer(texts['user_deleted'], reply_markup=keyboards.return_admin_markup())
    await state.clear()


# Ждём нажатия клавиши
@router.message(BotState.wait)
async def wait(message, state):
    await message.answer(texts['choose_option'], reply_markup=keyboards.found_user_markup())
