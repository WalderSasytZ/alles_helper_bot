from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from constants import months
import database
import api_requests


# Кнопка назад к главному меню
def return_menu_markup():
    row = [InlineKeyboardButton(text="← Назад", callback_data='menu')]
    return InlineKeyboardMarkup(inline_keyboard=[row])


# Кнопка назад в ЛК
def return_profile_markup():
    row = [InlineKeyboardButton(text="← Назад", callback_data='account')]
    return InlineKeyboardMarkup(inline_keyboard=[row])


# Кнопка назад к меню админа
def return_admin_markup():
    row = [InlineKeyboardButton(text="← Назад", callback_data='admin_menu')]
    return InlineKeyboardMarkup(inline_keyboard=[row])


# Кнопка назад к списку событий
def return_events_markup():
    row = [InlineKeyboardButton(text="← Назад", callback_data='print_events_0')]
    return InlineKeyboardMarkup(inline_keyboard=[row])


# Кнопка назад к списку событий
def return_questions_markup():
    row = [InlineKeyboardButton(text="← Назад", callback_data='print_questions_0')]
    return InlineKeyboardMarkup(inline_keyboard=[row])


# Главное меню
def main_menu_markup():
    row1 = [InlineKeyboardButton(text="💻 Личный кабинет",      callback_data='account')]
    row2 = [InlineKeyboardButton(text="📚 Избранные материалы", callback_data='materials')]
    row3 = [InlineKeyboardButton(text="❓ Вопросы и ответы",     callback_data='q_a')]
    row4 = [InlineKeyboardButton(text="🏫 Об Аллес",            callback_data='about_alles')]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3, row4])


# Меню личного кабинета
def account_menu_markup():
    row1 = [InlineKeyboardButton(text="🎓 Мои курсы",    callback_data='courses'),
            InlineKeyboardButton(text="⏰ Мои дедлайны", callback_data='deadlines')]
    row2 = [InlineKeyboardButton(text="⚙️ Интересы",     callback_data='interests'),
            InlineKeyboardButton(text="👤 Об аккаунте",  callback_data='about_acc')]
    row3 = [InlineKeyboardButton(text="← Назад",         callback_data='menu')]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3])


# Меню администратора
def admin_menu_markup():
    row1 = [InlineKeyboardButton(text="📆Создать",  callback_data='add_event'),
            InlineKeyboardButton(text="📆Вывести",  callback_data='print_events_0')]
    row2 = [InlineKeyboardButton(text="🔖Все теги", callback_data='print_tags')]
    row3 = [InlineKeyboardButton(text="❓ Вопросы пользователей", callback_data='print_questions_0')]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3])


# Меню главного администратора
def main_admin_menu_markup():
    row1 = [InlineKeyboardButton(text="👤Добавить", callback_data='add_user'),
            InlineKeyboardButton(text="👤Найти",    callback_data='find_user')]
    row2 = [InlineKeyboardButton(text="📆Создать",  callback_data='add_event'),
            InlineKeyboardButton(text="📆Вывести",  callback_data='print_events_0')]
    row3 = [InlineKeyboardButton(text="🔖Добавить", callback_data='menu_add_tags'),
            InlineKeyboardButton(text="🔖Вывести",  callback_data='print_tags'),
            InlineKeyboardButton(text="🔖Удалить",  callback_data='menu_delete_tags')]
    row4 = [InlineKeyboardButton(text="❓ Вопросы пользователей", callback_data='print_questions_0')]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3, row4])


# Меню найденного пользователя
def found_user_markup():
    row1 = [InlineKeyboardButton(text="👤Роль",    callback_data='set_role'),
            InlineKeyboardButton(text="👤Удалить", callback_data='delete_user')]
    row2 = [InlineKeyboardButton(text="← Назад",   callback_data='admin_menu')]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2])


# Меню удаления пользователя
def delete_user_markup():
    row = [InlineKeyboardButton(text="❌Удалить", callback_data='delete_user_confirmed'),
           InlineKeyboardButton(text="← Назад",   callback_data='admin_menu')]
    return InlineKeyboardMarkup(inline_keyboard=[row])


# Меню удаления события
def event_markup(event_id):
    row = [InlineKeyboardButton(text="❌Удалить", callback_data=f'delete_event_{event_id}'),
           InlineKeyboardButton(text="← Назад",   callback_data='print_events_0')]
    return InlineKeyboardMarkup(inline_keyboard=[row])


# Меню подтверждения удаления события
def event_delete_markup(event_id):
    row = [InlineKeyboardButton(text="❌Уверен", callback_data=f'event_deleted_{event_id}'),
           InlineKeyboardButton(text="← Назад",  callback_data='print_events_0')]
    return InlineKeyboardMarkup(inline_keyboard=[row])


# Меню подтверждения добавления новых тегов при создании события
def confirm_add_tags_markup():
    row = [InlineKeyboardButton(text="Добавить", callback_data='create_event_and_tags'),
           InlineKeyboardButton(text="← Назад",  callback_data='add_tags_again')]
    return InlineKeyboardMarkup(inline_keyboard=[row])


# Меню списка событий
async def print_events_markup(page_number):
    events_data = await database.get_events_data()
    events_num = len(events_data)
    pages_num = events_num // 10 + (events_num % 10 != 0)
    rows = []

    for event in events_data[10 * page_number: 10 * (page_number + 1)]:
        day = event['starts_at'].strftime("%d")
        month = months[event['starts_at'].strftime("%m")]
        time = event['starts_at'].strftime("%H:%M")
        row = [InlineKeyboardButton(text=f"({event['id']}) {day} {month} {time} {event['title']}",
                                    callback_data="event_data_" + str(event['id']))]
        rows.append(row)

    if pages_num > 1:
        pages_row = []
        if pages_num <= 7:
            for i in range(pages_num):
                pages_row.append(InlineKeyboardButton(text='✅' * (page_number == i) + f'{i + 1}',
                                                      callback_data=f'print_events_{i}'))
        else:
            if page_number < 4:
                for i in range(6):
                    pages_row.append(InlineKeyboardButton(text='✅' * (page_number == i) + f'{i + 1}',
                                                          callback_data=f'print_events_{i}'))
                pages_row.append(InlineKeyboardButton(text=f'...{pages_num}',
                                                      callback_data=f'print_events_{pages_num - 1}'))
            elif page_number >= pages_num - 4:
                pages_row.append(InlineKeyboardButton(text=f'{1}...',
                                                      callback_data=f'print_events_{0}'))
                for i in range(pages_num - 6, pages_num):
                    pages_row.append(InlineKeyboardButton(text='✅' * (page_number == i) + f'{i + 1}',
                                                          callback_data=f'print_events_{i}'))
            else:
                pages_row.append(InlineKeyboardButton(text=f'{1}...',
                                                      callback_data=f'print_events_{0}'))
                for i in range(page_number - 2, page_number + 3):
                    pages_row.append(InlineKeyboardButton(text='✅' * (page_number == i) + f'{i + 1}',
                                                          callback_data=f'print_events_{i}'))
                pages_row.append(InlineKeyboardButton(text=f'...{pages_num}',
                                                      callback_data=f'print_events_{pages_num - 1}'))
        rows.append(pages_row)

    rows.append([InlineKeyboardButton(text="← Назад", callback_data='admin_menu')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Меню списка формы вопросов
async def print_questions_markup(page_number):
    response = await api_requests.questions_data()

    rows = []
    if response:
        questions_data = await response.json()
        question_num = len(questions_data)
        pages_count = question_num // 10 + (question_num % 10 != 0)

        for question in questions_data[10 * page_number: 10 * (page_number + 1)]:
            row = [InlineKeyboardButton(text=f"{question['phone_number']} {question['name']}",
                                        callback_data=f"question_data_{question['id']}")]
            rows.append(row)

        if pages_count > 1:
            pages_row = []
            if pages_count <= 7:
                for i in range(pages_count):
                    pages_row.append(InlineKeyboardButton(text='✅' * (page_number == i) + f'{i + 1}',
                                                          callback_data=f'print_questions_{i}'))
            else:
                if page_number < 4:
                    for i in range(6):
                        pages_row.append(InlineKeyboardButton(text='✅' * (page_number == i) + f'{i + 1}',
                                                              callback_data=f'print_questions_{i}'))
                    pages_row.append(InlineKeyboardButton(text=f'...{pages_count}',
                                                          callback_data=f'print_questions_{pages_count - 1}'))
                elif page_number >= pages_count - 4:
                    pages_row.append(InlineKeyboardButton(text=f'{1}...',
                                                          callback_data=f'print_questions_{0}'))
                    for i in range(pages_count - 6, pages_count):
                        pages_row.append(InlineKeyboardButton(text='✅' * (page_number == i) + f'{i + 1}',
                                                              callback_data=f'print_questions_{i}'))
                else:
                    pages_row.append(InlineKeyboardButton(text=f'{1}...',
                                                          callback_data=f'print_questions_{0}'))
                    for i in range(page_number - 2, page_number + 3):
                        pages_row.append(InlineKeyboardButton(text='✅' * (page_number == i) + f'{i + 1}',
                                                              callback_data=f'print_questions_{i}'))
                    pages_row.append(InlineKeyboardButton(text=f'...{pages_count}',
                                                          callback_data=f'print_questions_{pages_count - 1}'))
            rows.append(pages_row)

    rows.append([InlineKeyboardButton(text="← Назад", callback_data='admin_menu')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Меню решения вопроса
def question_markup(question_id):
    row = [InlineKeyboardButton(text="Решено", callback_data=f'solve_question_{question_id}'),
           InlineKeyboardButton(text="← Назад", callback_data='print_questions_0')]
    return InlineKeyboardMarkup(inline_keyboard=[row])


# Меню подтверждения решения вопроса
def question_solve_markup(question_id):
    row = [InlineKeyboardButton(text="Решено", callback_data=f'question_solved_{question_id}'),
           InlineKeyboardButton(text="← Назад", callback_data='print_questions_0')]
    return InlineKeyboardMarkup(inline_keyboard=[row])
