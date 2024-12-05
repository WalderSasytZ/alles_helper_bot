from aiogram import Router
from aiogram.filters import Command
from datetime import datetime, timedelta

import database
import api_requests
import keyboards
from constants import texts
from bot_states import BotState

router = Router()


@router.message(Command("home"))
async def home_handler(message, state):
    await message.answer(texts["bot_reset"])
    await state.clear()


@router.message(Command("admin_menu"))
async def admin_menu_handler(message):
    # Проверяем права доступа на команду
    if await database.has_main_access(message.chat.id):
        await message.answer(texts['welcome_admin'], reply_markup=keyboards.main_admin_menu_markup())
    elif await database.has_admin_access(message.chat.id):
        await message.answer(texts['welcome_admin'], reply_markup=keyboards.admin_menu_markup())


@router.message(Command("start"))
async def start_handler(message, state):
    # Проверяем есть ли пользователь
    if await database.find_user(message.chat.id):
        await message.answer(texts['welcome'][0] + await database.get_name(message.chat.id) + texts['welcome'][1],
                             reply_markup=keyboards.main_menu_markup())
        await state.clear()
    else:
        await message.answer(texts["start_message"])
        await state.set_state(BotState.registration)


# ВРЕМЕННАЯ КОМАНДА пересоздания бд
@router.message(Command("recreate_db"))
async def recreate_db_handler(message):
    await database.recreate_tables()


# ВРЕМЕННАЯ КОМАНДА создания тестовых событий
@router.message(Command("create_events"))
async def create_event_handler(message):
    await database.delete_all_events()
    import string
    import random
    for i in range(150):
        title = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
        description = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
        date = datetime.now() + random.random() * (datetime.now() + timedelta(days=365) - datetime.now())
        await database.add_general_event(title, description, date)


# ВРЕМЕННАЯ КОМАНДА вывода пользователей сайта
@router.message(Command("api_print_users"))
async def get_data(message):
    users = await api_requests.get_users_data()

    if not users:
        await message.answer(texts["server_error"])
        return

    users_data = (await users.json())[:10]
    for user in users_data:
        await message.answer(str(dict(user)))


# ВРЕМЕННАЯ КОМАНДА вывода пользователей бота
@router.message(Command("print_users"))
async def print_user(message):
    users = (await database.get_users_data())[:7]
    for user in users:
        await message.answer(str(dict(user)))


# ВРЕМЕННАЯ КОМАНДА выдачи роли главного админа
@router.message(Command("give_me_rights"))
async def give_me_rights(message):
    # Добавляем в бд / меняем роль
    if not await database.find_user(message.chat.id):
        await database.add_user("unknown user", 2, message.chat.id)
    else:
        await database.set_role(2, message.chat.id)

    await message.answer(texts['role_is_set'])
