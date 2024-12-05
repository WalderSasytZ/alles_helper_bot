from aiogram import F, Router

import database
import keyboards
import api_requests
from handlers import BotState
from constants import texts, months

router = Router()


@router.callback_query(F.data == 'menu')
async def menu_callback(callback_query, state):
    name = await database.get_name(callback_query.from_user.id)
    await state.clear()
    await callback_query.message.edit_text(text=texts['welcome'][0] + name + texts['welcome'][1],
                                           reply_markup=keyboards.main_menu_markup())


@router.callback_query(F.data == 'account')
async def account_callback(callback_query):
    await callback_query.message.edit_text(text="💻 Личный кабинет", reply_markup=keyboards.account_menu_markup())


@router.callback_query(F.data == 'materials')
async def materials_callback(callback_query):
    await callback_query.message.edit_text(text="В разработке.", reply_markup=keyboards.return_menu_markup())


@router.callback_query(F.data == 'q_a')
async def q_a_callback(callback_query):
    await callback_query.message.edit_text(text="В разработке.", reply_markup=keyboards.return_menu_markup())


@router.callback_query(F.data == 'about_alles')
async def about_alles_callback(callback_query):
    await callback_query.message.edit_text(text=texts['about_alles'], reply_markup=keyboards.return_menu_markup())


@router.callback_query(F.data == 'courses')
async def q_a_callback(callback_query):
    await callback_query.message.edit_text(text="В разработке.", reply_markup=keyboards.return_profile_markup())


@router.callback_query(F.data == 'deadlines')
async def q_a_callback(callback_query):
    await callback_query.message.edit_text(text="В разработке.", reply_markup=keyboards.return_profile_markup())


@router.callback_query(F.data == 'interests')
async def q_a_callback(callback_query):
    await callback_query.message.edit_text(text="В разработке.", reply_markup=keyboards.return_profile_markup())


@router.callback_query(F.data == 'about_acc')
async def about_acc_callback(callback_query):
    website_id = await database.get_web_id(callback_query.message.chat.id)
    response = await api_requests.get_user_data(website_id)
    message_text = ""
    
    if response:
        user_data = await response.json()
        message_text = (f"Ваш id: {user_data['tg_chat_id']}\n" +
                        f"Имя: {user_data['first_name']} {user_data['last_name']}\n" +
                        f"Почта: {user_data['username']}\n" +
                        (user_data['grade'] is not None) * f"Класс: {user_data['grade']}")
    else:
        message_text = texts['server_error']

    await callback_query.message.edit_text(text=message_text, reply_markup=keyboards.return_profile_markup())


@router.callback_query(F.data == 'admin_menu')
async def admin_menu_callback(callback_query, state):
    await state.clear()
    # Проверяем права доступа на команду
    if await database.has_main_access(callback_query.from_user.id):
        await callback_query.message.edit_text(text=texts['welcome_admin'], reply_markup=keyboards.main_admin_menu_markup())
    elif await database.has_admin_access(callback_query.from_user.id):
        await callback_query.message.edit_text(text=texts['welcome_admin'], reply_markup=keyboards.admin_menu_markup())


@router.callback_query(F.data == 'add_user')
async def add_user_callback(callback_query, state):
    await callback_query.message.edit_text(text=texts['add_user_help'], reply_markup=keyboards.return_admin_markup())
    await state.set_state(BotState.add_user)

@router.callback_query(F.data == 'find_user')
async def find_user_callback(callback_query, state):
    await callback_query.message.edit_text(text=texts['find_user_help'], reply_markup=keyboards.return_admin_markup())
    await state.set_state(BotState.find_user)

@router.callback_query(F.data == 'set_role')
async def set_role_callback(callback_query, state):
    await callback_query.message.edit_text(text=texts['set_role_help'], reply_markup=keyboards.return_admin_markup())
    await state.set_state(BotState.set_role)


@router.callback_query(F.data == 'delete_user')
async def delete_user_callback(callback_query, state):
    await callback_query.message.edit_text(text=texts['delete_user_help'], reply_markup=keyboards.delete_user_markup())


@router.callback_query(F.data == 'delete_user_confirmed')
async def delete_user_confirmed_callback(callback_query, state):
    tg_chat_id = (await state.get_data())['find_user']

    # Проверяем наличие пользователя
    if not await database.find_user(tg_chat_id):
        await callback_query.message.edit_text(texts['user_404'], reply_markup=keyboards.return_admin_markup())
        return

    # Удаляем пользователя из бд
    await database.delete_user(tg_chat_id)
    await callback_query.message.edit_text(texts['user_deleted'], reply_markup=keyboards.return_admin_markup())
    await state.clear()


# Добавление события
@router.callback_query(F.data == 'add_event')
async def add_event_callback(callback_query, state):
    await callback_query.message.edit_text(text=texts['enter_event_title'], reply_markup=keyboards.return_admin_markup())
    await state.set_state(BotState.event_title)


# Добавление новых тегов в бд и создание события с ними
@router.callback_query(F.data == 'create_event_and_tags')
async def add_tags_again_callback(callback_query, state):
    new_tags = (await state.get_data())['event_add_tags'][0]
    entered_tags = (await state.get_data())['event_add_tags'][1]

    # Добавляем новые теги в бд
    for tag in new_tags:
        await database.add_tag(tag)

    # Создаём событие
    data = await state.get_data()
    event_id = await database.add_general_event(data['event_title'], data['event_description'], data['event_time'])

    # Добавляем связи тегов и событий в БД
    for tag in entered_tags:
        await database.create_tag_event(event_id, tag)

    await callback_query.message.edit_text(text=texts['event_created'], reply_markup=keyboards.return_admin_markup())
    await state.clear()


# Добавление тегов событию после отмены добавления новых тегов
@router.callback_query(F.data == 'add_tags_again')
async def add_tags_again_callback(callback_query, state):
    await callback_query.message.edit_text(text=texts['enter_tags'], reply_markup=keyboards.return_admin_markup())


# Добавление тегов главным админом
@router.callback_query(F.data == 'menu_add_tags')
async def add_tags_again_callback(callback_query, state):
    await callback_query.message.edit_text(text=texts['menu_add_tags'], reply_markup=keyboards.return_admin_markup())
    await state.set_state(BotState.menu_add_tags)


# Удаление тегов главным админом
@router.callback_query(F.data == 'menu_delete_tags')
async def delete_tags_again_callback(callback_query, state):
    await callback_query.message.edit_text(text=texts['menu_delete_tags'], reply_markup=keyboards.return_admin_markup())
    await state.set_state(BotState.menu_delete_tags)


# Вывод всех тегов
@router.callback_query(F.data == 'print_tags')
async def print_tags_callback(callback_query):
    tags = await database.get_tags_data()
    await callback_query.message.edit_text(text=(texts['tags_result'] + ', '.join(tag['name'] for tag in tags)),
                                           reply_markup=keyboards.return_admin_markup())


# Вывод информации о событии
@router.callback_query(F.data[:11] == 'event_data_')
async def event_data_callback(callback_query):
    event_id = int(callback_query.data.split('_')[-1])
    event = await database.get_event_data(event_id)

    a_day = event['added_at'].strftime("%d")
    a_month = months[event['added_at'].strftime("%m")]
    a_time = event['added_at'].strftime("%H:%M")
    s_day = event['starts_at'].strftime("%d")
    s_month = months[event['starts_at'].strftime("%m")]
    s_time = event['starts_at'].strftime("%H:%M")
    tags = await database.get_tags_of_event(event_id)

    message_text = (f"ID: ({event['id']})\n" +
                    f"Начало {s_day} {s_month} в {s_time}\n" +
                    f"Добавлено {a_day} {a_month} в {a_time}\n" +
                    f"Название: {event['title']}\n" +
                    f"Описание: {event['description']}\n" +
                    "Теги: " + ', '.join(tag['name'] for tag in tags))

    await callback_query.message.edit_text(text=message_text,
                                           reply_markup=keyboards.event_markup(event_id))


# Вывод заданной страницы списка событий
@router.callback_query(F.data[:13] == 'print_events_')
async def print_events_callback(callback_query):
    row_number = int(callback_query.data.split('_')[-1])
    await callback_query.message.edit_text(text=texts['events_printed'],
                                           reply_markup=await keyboards.print_events_markup(row_number))


# Подтверждение удалению события
@router.callback_query(F.data[:13] == 'delete_event_')
async def event_data_callback(callback_query):
    event_id = int(callback_query.data.split('_')[-1])
    event = await database.get_event_data(event_id)

    day = event['starts_at'].strftime("%d")
    month = months[event['starts_at'].strftime("%m")]
    time = event['starts_at'].strftime("%H:%M")
    message_text = texts['confirm_del_event'] + f"({event['id']}) {day} {month} {time} {event['title']}"

    await callback_query.message.edit_text(text=message_text,
                                           reply_markup=keyboards.event_delete_markup(event_id))


# Удаление события
@router.callback_query(F.data[:14] == 'event_deleted_')
async def event_data_callback(callback_query):
    event_id = int(callback_query.data.split('_')[-1])
    await database.delete_event(event_id)
    await callback_query.message.edit_text(text=texts['event_deleted'],
                                           reply_markup=keyboards.return_events_markup())


# Выводи меню с вопросами
@router.callback_query(F.data[:16] == 'print_questions_')
async def print_questions_callback(callback_query):
    page_num = int(callback_query.data.split('_')[-1])
    await callback_query.message.edit_text(text=texts['questions_printed'],
                                           reply_markup=await keyboards.print_questions_markup(page_num))


# Вывод информации о вопросе
@router.callback_query(F.data[:14] == 'question_data_')
async def question_data_callback(callback_query):
    question_id = int(callback_query.data.split('_')[-1])
    response = await api_requests.question_data(question_id)

    if not response:
        await callback_query.message.edit_text(text=texts['server_error'],
                                               reply_markup=keyboards.return_admin_markup())
        return

    question = await response.json()
    message_text = (texts['question_data'] +
                    (f"ID: ({question['id']})\n" +
                     f"Имя: {question['name']}\n" +
                     f"Телефон: {question['phone_number']}\n" +
                     f"Вопрос: {question['text_field']}\n\n"))

    await callback_query.message.edit_text(text=message_text, reply_markup=keyboards.question_markup(question_id))


# Решение вопроса
@router.callback_query(F.data[:15] == 'solve_question_')
async def question_data_callback(callback_query):
    question_id = int(callback_query.data.split('_')[-1])
    response = await api_requests.question_data(question_id)

    if not response:
        await callback_query.message.edit_text(text=texts['server_error'],
                                               reply_markup=keyboards.return_admin_markup())
        return

    question = await response.json()
    message_text = (texts['confirm_solve_quest'] +
                    (f"ID: ({question['id']})\n" +
                     f"Имя: {question['name']}\n" +
                     f"Телефон: {question['phone_number']}\n" +
                     f"Вопрос: {question['text_field']}\n\n"))

    await callback_query.message.edit_text(text=message_text, reply_markup=keyboards.question_solve_markup(question_id))


# Вопрос решён
@router.callback_query(F.data[:16] == 'question_solved_')
async def event_data_callback(callback_query):
    question_id = int(callback_query.data.split('_')[-1])
    await api_requests.questionForm_solved(question_id)
    await callback_query.message.edit_text(text=texts['question_solved'],
                                           reply_markup=keyboards.return_questions_markup())
