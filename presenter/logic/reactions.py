# -*- coding: utf-8 -*-
from presenter.config.config_func import Database, time_replace, is_suitable, feature_is_available
from view.output import delete, kick, send, promote, reply, send_video
from presenter.config.log import Loger, log_to
from presenter.config.files_paths import systems_file
import json

log = Loger(log_to)


def deleter(message):
    """Удаляет медиа ночью"""
    log.log_print("deleter invoked")
    database = Database()
    # Получаем из БД переменную, отвечающую за работу это функции
    delete_mode = database.get('config', ('var', 'delete'))['value']

    if not delete_mode:
        return None
    if time_replace(message.date)[1] >= 22 or time_replace(message.date)[1] < 8:  # Время, когда надо удалять
        database = Database()
        rank = database.get('members', ('id', message.from_user.id))['rank']
        if rank == 'Guest':
            # TODO бот делает это предупреждение не чаще раза в 24 часа на человека
            ans = "Э, нет, в такое время медиа нельзя присылать гостям чата. "
            ans += "Если вы не гость, то обратитесь к Дэ'Максу"
            send(message.chat.id, ans)
            delete(message.chat.id, message.message_id)


def new_member(message):
    """Реагирует на вход в чат"""
    log.log_print(f"{__name__} invoked")
    database = Database()
    member = message.new_chat_members[0]
    answer = ''
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    read_file = open(systems_file, 'r', encoding='utf-8')
    data = json.load(read_file)
    read_file.close()
    chat_configs = data[system]
    if database.get('members', ('id', member.id), ('rank', chat_configs['ranks'][0])) and feature_is_available(
            message.chat.id, system, 'violators_ban'):
        kick(message.chat.id, member.id)
    elif is_suitable(message, member, 'uber', loud=False) and feature_is_available(
            message.chat.id, system, 'admins_promote'):
        promote(message.chat.id, member.id,
                can_change_info=True, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=True)
        answer += "О, добро пожаловать, держи полную админку"
    elif is_suitable(message, member, 'boss', loud=False) and feature_is_available(
            message.chat.id, system, 'admins_promote'):
        promote(message.chat.id, member.id,
                can_change_info=False, can_delete_messages=True, can_invite_users=True,
                can_restrict_members=True, can_pin_messages=True, can_promote_members=False)
        answer += "О, добро пожаловать, держи админку"
    else:  # У нового участника нет особенностей
        answer = 'Добро пожаловать, {}'.format(member.first_name)
    sent = reply(message, answer)
    # Notify admins if admin's chat exists
    admin_place = database.get('systems', ('id', system))['admin_place']
    if admin_place:
        send(admin_place, '{} (@{}) [{}] теперь в {}'.format(member.first_name, member.username, member.id,
                                                         message.chat.title))
    return sent


def left_member(message):
    """Комментирует уход участника и прощается участником"""
    log.log_print("left_member invoked")
    database = Database()
    chat = database.get('chats', ('id', message.chat.id))
    system = chat['system']
    if chat['type'] == 'private':
        chat = chat['name']
    else:
        chat = '@' + chat['link']
    member = message.left_chat_member
    if message.from_user.id == member.id:  # Чел вышел самостоятельно
        reply(message, "Минус чувачок")
        send(member.id, 'До встречи в ' + chat)
    else:  # Чела забанили
        send_video(message.chat.id, "BAADAgADhgMAAgYqMUvW-ezcbZS2ohYE")
    # Notify admins if admin's chat exists
    admin_place = database.get('systems', ('id', system))['admin_place']
    if admin_place:
        send(admin_place, '{} (@{}) [{}] теперь не в {}'.format(member.first_name, member.username, member.id,
                                                            message.chat.title))
