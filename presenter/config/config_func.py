# -*- coding: utf-8 -*-
import sqlite3
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from presenter.config.files_paths import *
from view.output import *
from log import Loger, LOG_TO_CONSOLE
from config_var import superior_roles, admin_roles

log = Loger(LOG_TO_CONSOLE)

def is_admin(message, superior=False):
    log.log_print("Проверяем пользователя {0} на админку".format(message.from_user.username))
    database = Database()
    rank = database.get(message.from_user.id)[3]  # Получаем его звание
    del database
    if superior:
        if rank in superior_roles:
            return True
        else:
            reply(message, "Э, нет, эта кнопка только для Лидера и его Заместителя")
            return False
    elif rank in admin_roles:
        return True
    else:
        reply(message, "Э, нет, эта кнопка только для админов")
        return False


def cooldown(message):  # TODO если команда используется одновременно один из челов нарывается на кулдаун
    if 'есть один мем' in message.text.lower():
        analyze = '/meme'
    else:
        analyze = message.text.split()[0]  # Первое слово в строке
        if '@' in analyze:
            analyze = analyze.split('@')[0]  # Убираем собачку и то, что после неё
    log.log_print("Вызвана функция cooldown с параметрами {}:{}".format(message.from_user.id, message.text))
    database = Database()
    commands = database.get_many(message.from_user.id, 'cooldown', 'id')
    print(commands)
    for command in commands:
        if analyze in command:
            time_passed = message.date - command[2]
            if time_passed < 60:  # Кулдаун не прошёл
                answer = "Воу, придержи коней, ковбой. Ты сможешь воспользоваться этой командой только "
                answer += "через {} секунд 🤠".format(60 - time_passed)
                reply(message, answer)
                del database
                return False
            else:  # Кулдаун прошёл
                database.change(message.date, command[2], 'cooldown', 'time', 'time')
                del database
                return True
    else:  # Чел впервые пользуется коммандой
        print('???')
        database.append((message.from_user.id, analyze, message.date), 'cooldown')
        del database
        return True


def time_replace(seconds):
    seconds += 3*60*60
    minutes = seconds//60
    seconds %= 60
    hours = minutes//60
    minutes %= 60
    days = hours//60
    hours %= 24
    return days, hours, minutes, seconds


def error(message, e):
    """Уведомляет Дэ'Максимилианстера об ошибке, не привёвшей к вылету"""
    send(381279599, "Произошла ошибка")
    send(381279599, e)
    reply(message, "У меня произошла непроизвольная дефекация")
    print(e)


def in_mf(message, or_private=True):
    """Позволяет регулировать использование команл вне чатов и в личке"""
    database = Database()
    if database.get(message.chat.id, 'chats'):  # Команда вызвана в системе МФ2
        counter(message)  # Отправляем сообщение на учёт в БД
        return True
    elif message.chat.type == 'private':  # Команда вызвана в личке
        if or_private:  # Команда одобрена для использования в личке (например /minet)
            return True
        else:  # Команда не одобрена для использования в личке (например /ban)
            person = message.from_user
            send(381279599, "Некто {} ({}) [{}] попыталcя использовать команду {} в личке"
                            .format(person.first_name, person.username, person.id, message.text))
            reply(message, "Эта команда отключена в ЛС")
            return False
    try:
        send(381279599, "Жалкие завистники из чата с ID {} и названием {} попытались мной воспользоваться"
                        .format(message.chat.id, message.chat.title))
        reply(message, "Я тут не работаю. Зато я работаю в @MultiFandomRu")
    except Exception as e:
        print(e)
    return False


def counter(message):
    """Подсчитывает сообщения, отправленные челом"""
    database = Database()
    if message.new_chat_members:
        person = message.new_chat_members[0]
    else:
        person = message.from_user
    if database.get(person.id) is None:  # Нет такой записи
        answer = 'Добро пожаловать в наш чат! Напиши мне в личку и в будущем получишь доступ '
        answer += 'к различным функциям. Читай закреп, веди себя хорошо, приятного времяпровождения!'
        reply(message, answer)
        try:
            person = (person.id, str(person.username), person.first_name, 'Гость', 1, 0, 0)
            database.append(person)
        except Exception as e:
            error(message, e)
    else:  # Чел есть в БД
        value = database.get(person.id)[4] + 1
        database.change(value, person.id, 'members', 'messages', 'id')
    del database


# TODO перенести все голосовашки в базу данных или ещё куда-то (JSON)
def create_vote(vote_message):
    """Создаёт голосовашку"""
    log.log_print("Создаём голосовашку с текстом: "+vote_message.text)
    # TODO Параметр purpose, отвечающий за действие, которое надо сделать при закрытии голосовашки
    file = open(votes_file, 'r')
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votes_shelve[vote_message.message_id] = {"time": vote_message.date, "text": vote_message.text,
                                             "favor": {}, "against": {}, "abstain": {}}
    file = open(votes_file, 'w')
    file.write(str(votes_shelve))
    file.close()


def create_multi_vote(vote_message):
    """Создаёт мульти-голосовашку"""
    log.log_print("Создаём мульти-голосовашку с текстом: "+vote_message.text)
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_option{}'.format(vote_message.message_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    file = open(multi_votes_file)
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votes_shelve[vote_message.message_id] = {"text": vote_message.text, "votes": [], "keyboard": [],
                                             "chat": vote_message.chat.id}
    file = open(multi_votes_file, 'w')
    file.write(str(votes_shelve))
    file.close()
    edit_markup(vote_message.chat.id, vote_message.message_id, reply_markup=keyboard)


def create_adapt_vote(vote_message):
    """Создаёт адапт-голосовашку"""
    log.log_print("Создаём адапт-голосовашку с текстом: "+vote_message.text)
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_adapt_option{}'.format(vote_message.message_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    file = open(adapt_votes_file)
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votes_shelve[vote_message.message_id] = {"text": vote_message.text, "votes": [], "keyboard": [],
                                             "chat": vote_message.chat.id}
    file = open(adapt_votes_file, 'w')
    file.write(str(votes_shelve))
    file.close()
    edit_markup(vote_message.chat.id, vote_message.message_id, reply_markup=keyboard)


def update_multi_vote(vote_id):
    """Обновляет мульти-голосовашку"""
    log.log_print("обновляем мульти-голосовашку с id: "+str(vote_id))
    file = open(multi_votes_file)
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votey = dict(votes_shelve[vote_id])
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_option{}'.format(vote_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    for i in votey['keyboard']:
        keyboard.add(InlineKeyboardButton(i, callback_data='mv_'+str(votey['keyboard'].index(i))))
    # Меняем текст голосовашки
    text = votey["text"]
    for i in votey['votes']:
        text += '\n{}: '.format(i[0]) + ', '.join(i[1].values())
    try:
        edit_text(text=text, chat_id=votey['chat'], message_id=vote_id, reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        print(e)


def update_adapt_vote(vote_id):
    """Обновляет адапт голосовашку"""
    log.log_print("обновляем адапт-голосовашку с id: "+str(vote_id))
    file = open(adapt_votes_file)
    votes_shelve = file.read()
    if votes_shelve:
        votes_shelve = eval(votes_shelve)
    else:
        votes_shelve = {}
    file.close()
    votey = dict(votes_shelve[vote_id])
    keyboard = InlineKeyboardMarkup()
    url = 'https://t.me/multifandomrubot?start=new_adapt_option{}'.format(vote_id)
    keyboard.row_width = 1
    keyboard.add(InlineKeyboardButton("Предложить вариант", url=url))
    for i in votey['keyboard']:
        keyboard.add(InlineKeyboardButton(i, callback_data='av_'+str(votey['keyboard'].index(i))))
    # Меняем текст голосовашки
    text = votey["text"]
    for i in votey['votes']:
        text += '\n{}: '.format(i[0]) + ', '.join(i[1].values())
    try:
        edit_text(text=text, chat_id=votey['chat'], message_id=vote_id, reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        print(e)


class Database:
    """Управление базой данных"""

    def __init__(self):
        """Подключается к базе данных"""
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def __del__(self):
        """Отключается от базы данных"""
        self.connection.close()  # Закрываем БД

    def get(self, value, table='members', column='id'):
        """Читает запись в базе данных"""
        sql = "SELECT * FROM {} WHERE {}='{}'".format(table, column, value)
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def get_many(self, value, table='chats', column='purpose'):
        """Читает несколько записей в базе данных"""
        sql = "SELECT * FROM {} WHERE {}='{}'".format(table, column, value)
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_all(self, table):
        """Читает все записи в одной таблице базы данных"""
        sql = "SELECT rowid, * FROM {} ORDER BY id".format(table)
        all_list = []
        for element in self.cursor.execute(sql):
            all_list.append(element[1:])  # Первый элемент это бесполезный номер
        return all_list

    def change(self, set_value, where_value, table='members', set_column='messages', where_column='id'):
        """Меняет что-то в базе данных"""
        # Одинарные кавычки в sql очень важны
        sql = """
        UPDATE {}
        SET {} = '{}'
        WHERE {} = '{}'
        """.format(table, set_column, set_value, where_column, where_value)
        self.cursor.execute(sql)
        self.connection.commit()  # Сохраняем изменения

    def append(self, values, table='members'):
        """Добавляет запись в базу данных"""
        try:
            print('Таки добавляю запись')
            sql = """
            INSERT INTO {}
            VALUES {}
            """.format(table, values)
            self.cursor.execute(sql)
        except Exception as e:
            print(e)
        self.connection.commit()  # Сохраняем изменения
