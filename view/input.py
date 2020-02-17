""" All bot message and call handlers are here """
from view.output import reply, answer_callback, send_document
from presenter.config.token import BOT
from presenter.config.config_func import in_mf, cooldown, rank_superiority, \
    int_check, is_suitable, in_system_commands, is_correct_message, remove_slash_and_bot_mention, \
    convert_command_to_storage_content, language_analyzer
import presenter.config.config_func as config_func
from presenter.logic.elite import elite
from presenter.logic.boss_commands import ban, add_chat, add_admin_place, chat_options, \
    system_options, warn, unwarn, message_change, money_pay, rank_changer, mute, money_mode_change,\
    money_emoji, money_name, update_all_members, add_stuff_to_storage
from presenter.logic.complicated_commands import adequate, inadequate, response, insult, \
    ironic, non_ironic, place_here, mv, av, add_vote, vote, captcha_completed, captcha_failed
import presenter.logic.reactions as reactions
from presenter.logic.standart_commands import helper, send_me, send_meme, minet, money_give, \
    language_getter, month_set, day_set, admins, chat_check, \
    anon_message, system_check, money_helper, send_stuff_from_storage, send_some_top
from presenter.logic.start import starter
from presenter.config.log import Loger, log_to
from presenter.config.config_var import features_defaulters, features_oners, features_offers, \
    system_features_offers, system_features_oners, porn_adders, stuff_adders, all_content_types, \
    commands_to_add_stuff, commands_to_add_vulgar_stuff
from presenter.config.files_paths import VOTES_FILE, DATABASE_FILE, ADAPT_VOTES_FILE, \
    MULTI_VOTES_FILE, SYSTEMS_FILE, STORAGE_FILE
import presenter.logic.developer_commands as developer_commands

# TODO Убрать этот ебучий срач
LOG = Loger(log_to)
WORK = True

# Реакции на медиа, новых участников и выход участников


@BOT.message_handler(content_types=['migrate_from_chat_id'])
def chat_id_update_handler(message):
    """ Update chat ID """
    LOG.log_print("chat_id_update_handler invoked")
    reactions.chat_id_update(message)


@BOT.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    """Реагирует на вход в чат"""
    LOG.log_print("new_member_handler invoked")
    person = message.new_chat_members[0]
    if in_mf(message, command_type=None, or_private=False):
        reactions.new_member(message, person)


@BOT.message_handler(content_types=['left_chat_member'])
def left_member_handler(message):
    """Комментирует уход участника и прощается участником"""
    LOG.log_print("left_member_handler invoked")
    if in_mf(message, command_type=None, or_private=False, loud=False):
        reactions.left_member(message)


# Элитарные команды


@BOT.message_handler(commands=['elite'])
def elite_handler(message):
    """ Runs an Elite test """
    LOG.log_print("elite_handler invoked")
    if message.chat.type == 'private':  # Тест на элитность можно провести только в личке у бота
        elite(message)
    else:
        reply(message, "Напиши мне это в личку, я в чате не буду этим заниматься")


# Админские обычные команды


# @bot.message_handler(commands=['search'])
# def chat_search_handler(message):
#     # Ищет чаты
#     if in_mf(message) and rank_required(message, "Админ"):
#         chat_search(message)


@BOT.message_handler(commands=commands_to_add_vulgar_stuff)
def upload_vulgar_stuff_to_storage_handler(message):
    """ Add vulgar stuff to a media storage """
    LOG.log_print("upload_vulgar_stuff_to_storage_handler invoked")
    command = convert_command_to_storage_content(message.text)
    if in_mf(message, 'erotic_commands'):
        if message.from_user.id in porn_adders:
            add_stuff_to_storage(message, command)
        else:
            reply(message, "Не-а, вы не числитесь в рядах добавлятелей 'контента'")


@BOT.message_handler(commands=commands_to_add_stuff)
def upload_stuff_to_storage_handler(message):
    """ Add stuff to a media storage """
    LOG.log_print("upload_stuff_to_storage_handler invoked")
    command = convert_command_to_storage_content(message.text)
    if in_mf(message, command_type=None):
        if message.from_user.id in stuff_adders:
            add_stuff_to_storage(message, command)
        else:
            reply(message, "Не-а, вы не числитесь в рядах добавлятелей контента")


@BOT.message_handler(commands=['update'])
def update_all_members_handler(message):
    """ Updates members database """
    LOG.log_print("update_all_members_handler invoked")
    if in_mf(message, 'boss_commands', or_private=False) and is_suitable(message, message.from_user,
                                                                         'boss'):
        update_all_members(message)


@BOT.message_handler(commands=['warn'])
def warn_handler(message):
    """Даёт участнику предупреждение"""
    LOG.log_print("warn_handler invoked")
    if in_mf(message, 'boss_commands', or_private=False) and is_suitable(message, message.from_user,
                                                                         'boss'):
        rep = message.reply_to_message
        if rep:
            analyzer = config_func.Analyzer(message, default_value=1, value_positive=True)
            parameters_dictionary = analyzer.parameters_dictionary
            if analyzer.check_person(rep.from_user, False, False) \
                    and rank_superiority(message, rep.from_user):
                if parameters_dictionary:
                    warn(message, rep.from_user, parameters_dictionary)
        else:
            reply(message,
                  "Надо ответить на сообщение с актом преступления, чтобы переслать контекст в\
                   хранилище")


@BOT.message_handler(commands=['unwarn'])
def unwarn_handler(message):
    """Снимает с участника предупреждение"""
    LOG.log_print("unwarn_handler invoked")
    if in_mf(message, 'boss_commands', or_private=False) and is_suitable(message, message.from_user,
                                                                         'boss'):
        analyzer = config_func.Analyzer(message, default_value=1, value_positive=True)
        person = analyzer.return_target_person()
        if person:
            unwarn(message, person, analyzer.parameters_dictionary)


@BOT.message_handler(commands=['ban'])
def ban_handler(message):
    """ Ban member """
    LOG.log_print(f"ban_handler invoked")
    if in_mf(message, 'boss_commands', or_private=False) and is_suitable(message, message.from_user,
                                                                         'boss'):
        person = config_func.Analyzer(message, value_necessary=False).return_target_person()
        if person and rank_superiority(message, person):
            ban(message, person)


@BOT.message_handler(commands=['kick'])
def kick_handler(message):
    """ Kicks member """
    LOG.log_print(f"kick_handler invoked")
    if in_mf(message, 'boss_commands', or_private=False) and is_suitable(message, message.from_user,
                                                                         'boss'):
        person = config_func.Analyzer(message, value_necessary=False).return_target_person()
        if person and rank_superiority(message, person):
            ban(message, person, unban_then=True)


@BOT.message_handler(commands=['mute'])
def mute_handler(message):
    """ Mutes member """
    LOG.log_print("mute_handler invoked")
    if in_mf(message, "boss_commands", or_private=False) and is_suitable(message, message.from_user,
                                                                         'boss'):
        analyzer = config_func.Analyzer(message, default_value=1, value_positive=True)
        person = analyzer.return_target_person()
        parameters_dictionary = analyzer.parameters_dictionary
        if person and rank_superiority(message, person) and parameters_dictionary:
            mute(message, person, parameters_dictionary)


@BOT.message_handler(commands=['pay'])
def money_pay_handler(message):
    """ Give money from the treasury to the member """
    LOG.log_print(f"money_pay_handler invoked")
    if in_mf(message, 'financial_commands', or_private=False) \
            and is_suitable(message, message.from_user, 'boss'):
        analyzer = config_func.Analyzer(message)
        person = analyzer.return_target_person(to_self=True)
        parameters_dictionary = analyzer.parameters_dictionary
        if person and parameters_dictionary:
            money_pay(message, person, parameters_dictionary)


# @bot.message_handler(commands=['delete_mode'])
# def deleter_mode_handler(message):
#     LOG.log_print(f"{__name__} invoked")
#     if in_mf(message, 'boss_commands', False) and is_suitable(message, message.from_user, "boss"):
#         deleter_mode(message)


@BOT.message_handler(func=lambda message: in_system_commands(message))
def rank_changer_handler(message):
    """Sets person's rank to guest"""
    LOG.log_print("rank_changer_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        # TODO Сделать так, чтоб добавлять можно было только лидера
        if message.from_user.id == 381279599:
            person = config_func.Analyzer(message, value_necessary=False).return_target_person()
            if person:
                rank_changer(message, person)
        elif is_suitable(message, message.from_user, 'boss'):
            person = config_func.Analyzer(message, value_necessary=False).return_target_person()
            if person and rank_superiority(message, person):
                rank_changer(message, person)


@BOT.message_handler(commands=['messages'])
def messages_change_handler(message):
    """Меняет запись в БД о количестве сообщений чела"""
    LOG.log_print(f"messages_change_handler invoked")
    if in_mf(message, 'boss_commands', or_private=False) and is_suitable(message, message.from_user,
                                                                         "boss"):
        analyzer = config_func.Analyzer(message, value_positive=True)
        person = analyzer.return_target_person()
        parameters_dictionary = analyzer.parameters_dictionary
        if person and parameters_dictionary:
            message_change(message, person, parameters_dictionary)


@BOT.message_handler(commands=['add_chat'])
def add_chat_handler(message):  # TODO Она работает в личке, а не должна
    """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
    LOG.log_print(f"add_chat_handler invoked")
    add_chat(message)


@BOT.message_handler(commands=['admin_place'])
def add_admin_place_handler(message):
    """Add admin place to system"""
    LOG.log_print("add_admin_place_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message,
                                                                           message.from_user,
                                                                           "chat_changer"):
        add_admin_place(message)


@BOT.message_handler(commands=['money_on', 'money_off'])
def money_mode_change_handler(message):
    """ Enable or disable money system """
    LOG.log_print("money_mode_change_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message,
                                                                           message.from_user,
                                                                           "chat_changer"):
        money_mode_change(message)


@BOT.message_handler(commands=['m_emoji'])
def money_emoji_handler(message):
    """ Put emoji to indicate the amount of currency """
    LOG.log_print("money_emoji_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message,
                                                                           message.from_user,
                                                                           "chat_changer"):
        money_emoji(message)


@BOT.message_handler(commands=['m_name'])
def money_name_handler(message):
    """ Set currency name """
    LOG.log_print("money_name_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message,
                                                                           message.from_user,
                                                                           "chat_changer"):
        money_name(message)


@BOT.message_handler(commands=features_offers + features_oners + features_defaulters)
def chat_options_handler(message):
    """ Change chat options """
    LOG.log_print("chat_options_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message,
                                                                           message.from_user,
                                                                           "chat_changer"):
        chat_options(message)


@BOT.message_handler(commands=system_features_oners + system_features_offers)
def system_options_handler(message):
    """ Change chat system options """
    LOG.log_print("system_options_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message,
                                                                           message.from_user,
                                                                           "chat_changer"):
        system_options(message)


# @bot.message_handler(commands=['change_database'])
# def database_changer_handler(message):
#     """Добавляет чат в базу данных чатов, входящих в систему МФ2"""
#     LOG.log_print(f"{__name__} invoked")
#     if rank_required(message, "Deputy"):
#         database_changer()


# Составные команды

@BOT.callback_query_handler(func=lambda call: call.data == 'captcha')
def captcha_completed_handler(call):
    """ It is executing when new member passes the captcha """
    LOG.log_print("captcha_completed_handler invoked")
    captcha_completed(call)


@BOT.callback_query_handler(func=lambda call: call.data == 'captcha_fail')
def captcha_failed_handler(call):
    """ It is executing when new member fails the captcha """
    LOG.log_print("captcha_failed_handler invoked")
    captcha_failed(call)


@BOT.callback_query_handler(func=lambda call: 'adequate' in call.data and call.data != 'inadequate')
def adequate_handler(call):
    """Вариант адекватен"""
    LOG.log_print(f"adequate_handler invoked")
    adequate(call)


@BOT.callback_query_handler(func=lambda call: call.data == 'inadequate')
def inadequate_handler(call):
    """Вариант неадекватен"""
    LOG.log_print(f"inadequate_handler invoked")
    inadequate(call)


@BOT.inline_handler(lambda query: query.query == 'test')
def response_handler(inline_query):
    """Тестовая инлайновая команда, бесполезная"""
    LOG.log_print(f"response_handler invoked")
    response(inline_query)


@BOT.message_handler(regexp='Признаю оскорблением')
def insult_handler(message):  # TODO В частных чатах бот не умеет указать ссылку нормально
    # TODO Проверка на наличие админосостава
    """Спращивает, иронично ли признание оскорблением"""
    LOG.log_print(f"insult_handler invoked")
    if in_mf(message, command_type=None, or_private=False) and is_suitable(message,
                                                                           message.from_user,
                                                                           "standart"):
        insult(message)


@BOT.callback_query_handler(
    func=lambda call: call.data == 'non_ironic')  # триггерится, когда нажата кнопка "Нет"
def non_ironic_handler(call):
    """Реакция, если обвинение было неироничным"""
    LOG.log_print(f"non_ironic_handler invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        non_ironic(call)
    else:
        answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@BOT.callback_query_handler(
    func=lambda call: call.data == 'ironic')  # триггерится, когда нажата кнопка "Да"
def ironic_handler(call):
    """Реакция, если обвинение было ироничным"""
    LOG.log_print(f"ironic_handler invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        ironic(call)
    else:
        answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@BOT.message_handler(commands=['vote', 'multi_vote', 'adapt_vote'])
def vote_handler(message):
    """Генерирует голосовашку"""
    LOG.log_print(f"vote_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        vote(message)


@BOT.callback_query_handler(func=lambda call: 'here' in call.data or 'nedostream' in call.data)
def place_here_handler(call):
    """Выбирает, куда прислать голосовашку"""
    LOG.log_print(f"place_here_handler invoked")
    # Проверка, нажал ли на кнопку не тот, кто нужен
    if call.message.reply_to_message.from_user.id == call.from_user.id:
        place_here(call)
    else:
        answer_callback(call.id, "Э, нет, эта кнопка не для тебя")


@BOT.callback_query_handler(func=lambda call: 'mv_' in call.data)
def mv_handler(call):
    """Обновляет мульти-голосовашку"""
    LOG.log_print(f"mv_handler invoked")
    # TODO Убрать привязку к МФным голосовашкам
    if call.chat_instance != "-8294084429973252853" or is_suitable(call, call.from_user,
                                                                   "advanced"):
        mv(call)


@BOT.callback_query_handler(func=lambda call: 'av_' in call.data)
def av_handler(call):
    """Обновляет адапт-голосовашку"""
    LOG.log_print(f"av_handler invoked")
    if call.chat_instance != "-8294084429973252853" or is_suitable(call, call.from_user,
                                                                   "advanced"):
        av(call)


@BOT.callback_query_handler(
    func=lambda call: call.data == 'favor' or call.data == 'against' or call.data == 'abstain')
def add_vote_handler(call):
    """Вставляет голос в голосоовашку"""
    LOG.log_print("add_vote_handler invoked")
    if call.chat_instance != "-8294084429973252853" or is_suitable(call, call.from_user,
                                                                   "advanced"):
        add_vote(call)


# Простые команды и старт


# TODO Это блять не простая команда, а админская
@BOT.message_handler(commands=['lang'])
def language_getter_handler(message):
    """Gets the language of the chat"""
    LOG.log_print("language_getter_handler invoked")  # TODO Более удобную ставилку языков
    if in_mf(message, command_type=None, or_private=True):
        if message.chat.id > 0 or is_suitable(message, message.from_user, 'boss'):
            language_getter(message)


@BOT.message_handler(commands=['start'])
def starter_handler(message):
    """Запуск бота в личке, в чате просто реагирует"""
    LOG.log_print("starter_handler invoked")
    if is_correct_message(message) and in_mf(message, command_type=None):
        starter(message)


@BOT.message_handler(commands=['help'])
def helper_handler(message):
    """Предоставляет человеку список команд"""
    LOG.log_print("helper_handler invoked")
    if is_correct_message(message) and in_mf(message, command_type=None):
        helper(message)


@BOT.message_handler(commands=['money_help', 'help_money'])
def money_helper_handler(message):
    """Financial instructions"""
    LOG.log_print("money_helper_handler invoked")
    if in_mf(message, command_type=None):
        money_helper(message)


@BOT.message_handler(commands=['id'])
def show_id_handler(message):
    """Присылает различные ID'шники, зачастую бесполезные"""
    LOG.log_print(f"show_id_handler invoked")
    if in_mf(message, command_type=None):
        developer_commands.show_id(message)


@BOT.message_handler(commands=['echo'])
def echo_message_handler(message):
    """ Repeats message """
    LOG.log_print("echo_message_handler invoked")
    if in_mf(message, command_type=None):
        developer_commands.echo_message(message)


@BOT.message_handler(commands=['clear'])
def clear_echo_message_handler(message):
    """ Clears echo messages """
    LOG.log_print("clear_echo_message_handler invoked")
    if in_mf(message, command_type=None):
        developer_commands.clear_echo_message(message)


@BOT.message_handler(commands=['html'])
def html_echo_message_handler(message):
    """ Repeats message with HTML message markup """
    LOG.log_print("html_echo_message_handler invoked")
    if in_mf(message, command_type=None):
        developer_commands.html_echo_message(message)


@BOT.message_handler(commands=['minet', 'french_style_sex', 'blowjob'])
def minet_handler(message):
    """Приносит удовольствие"""
    LOG.log_print(f"minet_handler invoked")
    if is_correct_message(message) and in_mf(message, 'standart_commands'):
        language = language_analyzer(message, only_one=True)
        if language and cooldown(message, 'minet'):
            minet(message, language)


@BOT.message_handler(commands=['drakken', 'art'])
def send_stuff_from_storage_handler(message):
    """Send random media from the storage"""
    LOG.log_print("send_stuff_from_storage_handler invoked")
    command = remove_slash_and_bot_mention(message.text)
    if in_mf(message, 'standart_commands') and cooldown(message, command):
        send_stuff_from_storage(message, command)


@BOT.message_handler(commands=['breasts', 'ass'])
def send_vulgar_stuff_from_storage_handler(message):
    """ Send vulgar stuff from media storage """
    LOG.log_print("send_vulgar_stuff_from_storage_handler invoked")
    command = remove_slash_and_bot_mention(message.text)
    if in_mf(message, 'erotic_commands') and cooldown(message, command, timeout=60):
        send_stuff_from_storage(message, command)


@BOT.message_handler(regexp='есть один мем')
@BOT.message_handler(commands=['meme'])
def send_meme_handler(message):
    """Присылает мем"""
    LOG.log_print(f"send_meme_handler invoked")
    if in_mf(message, 'standart_commands') and cooldown(message, 'meme'):
        send_meme(message)


@BOT.message_handler(commands=['me', 'check', 'check_me', 'check_ebalo'])
def send_me_handler(message):
    """Присылает человеку его запись в БД"""
    LOG.log_print(f"send_me_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        person = config_func.Analyzer(message, value_necessary=False).return_target_person(
            to_self=True)
        if person:
            send_me(message, person)


@BOT.message_handler(commands=['members'])
def all_members_handler(message):
    """Присылает человеку все записи в БД"""
    LOG.log_print("all_members_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        if message.chat.id != -1001444879250 or is_suitable(message, message.from_user, 'boss'):
            language = language_analyzer(message, only_one=True)
            if language:
                send_some_top(message, language, '{index}. <code>{p_id}</code> {p_link}\n')


@BOT.message_handler(commands=['give'])
def money_give_handler(message):
    """Обмен денег между пользователями"""
    LOG.log_print(f"money_give_handler invoked")
    if in_mf(message, 'financial_commands', or_private=False):
        analyzer = config_func.Analyzer(message)
        person = analyzer.return_target_person()
        parameters_dictionary = analyzer.parameters_dictionary
        if person and parameters_dictionary:
            money_give(message, person, parameters_dictionary)


@BOT.message_handler(commands=['top'])
def money_top_handler(message):
    """Топ ЯМ"""
    LOG.log_print("money_top_handler invoked")
    if in_mf(message, 'financial_commands', or_private=False):
        language = language_analyzer(message, only_one=True)
        if language:
            send_some_top(message, language, '{index}. {p_link} — {money} {m_emo}\n',
                          start='Бюджет: {bot_money} {m_emo}\n\n', sort_key=lambda x: x['money'],
                          filter_f=lambda x: x['money'] > 0, to_private=False)


@BOT.message_handler(commands=['warns'])
def warns_top_handler(message):
    """ Show all warns """
    LOG.log_print('warns_top_handler invoked')
    if in_mf(message, command_type=None, or_private=False):
        language = language_analyzer(message, only_one=True)
        if language:
            send_some_top(message, language, '{index}. {p_link} — {warns} ⛔️\n',
                          start='Количество варнов:\n\n',
                          sort_key=lambda x: x['warns'], filter_f=lambda x: x['warns'] > 0,
                          to_private=False)


@BOT.message_handler(commands=['messages_top'])
def messages_top_handler(message):
    """Messages top"""
    LOG.log_print("messages_top_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        language = language_analyzer(message, only_one=True)
        if language:
            if is_suitable(message, message.from_user, 'boss', loud=False):
                send_some_top(message, language, '{index}. {p_link} — {messages} сообщ.\n',
                              sort_key=lambda x: x['messages'],
                              filter_f=lambda x: x['messages'] > 10)
            else:
                send_some_top(message, language, '{index}. {p_link} — {messages} сообщ.\n',
                              sort_key=lambda x: x['messages'],
                              filter_f=lambda x: x['messages'] > 10,
                              to_private=False, max_people=5)


@BOT.message_handler(commands=['month'])
def month_set_handler(message):
    """Set month of person's birthday"""
    LOG.log_print("month_set_handler invoked")
    if in_mf(message, command_type=None):
        month = int_check(message.text.split()[-1], positive=True)
        if month and 1 <= month <= 12:
            month_set(message, month)
        else:
            reply(message,
                  "Последнее слово должно быть положительным числом от 1 до 12 — номером месяца")


@BOT.message_handler(commands=['day'])
def day_set_handler(message):
    """Set day of person's birthday"""
    LOG.log_print("day_set_handler invoked")
    if in_mf(message, command_type=None):
        day = int_check(message.text.split()[-1], positive=True)
        if day and 1 <= day <= 31:
            language = language_analyzer(message, only_one=True)
            if language:
                day_set(message, day, language)
        else:
            reply(message,
                  "Последнее слово должно быть положительным числом от 1 до 31 — номером дня")


@BOT.message_handler(commands=['bdays', 'birthdays'])
def birthday_handler(message):
    """Show the nearest birthdays"""
    LOG.log_print(f"birthday_handler invoked")
    if in_mf(message, command_type=None):
        language = language_analyzer(message, only_one=True)
        if language:
            send_some_top(message, language, '{index}. {p_link} — {day} {month}\n',
                          sort_key=lambda x: 100 * x['month_birthday'] + x['day_birthday'],
                          filter_f=lambda x: x['month_birthday'] > 0 and x['day_birthday'] > 0,
                          to_private=False, reverse=False)


@BOT.message_handler(commands=['admins', 'report'])
def admins_handler(message):
    """Ping admins"""
    LOG.log_print("admins_handler invoked")
    if in_mf(message, command_type=None) and is_suitable(message, message.from_user, "standart") \
            and cooldown(message, 'admins', 300):
        admins(message)


@BOT.message_handler(commands=['chat'])
def chat_check_handler(message):
    """Show options of the current chat"""
    LOG.log_print("chat_check_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        chat_check(message)


@BOT.message_handler(commands=['system'])
def system_check_handler(message):
    """Show options of the current chat"""
    LOG.log_print("system_check_handler invoked")
    if in_mf(message, command_type=None, or_private=False):
        system_check(message)


# @bot.message_handler(commands=['chats'])
# def chats_handler(message):
#     """Send chat list"""
#     if in_mf(message, 'standart_commands'):
#         chats(message)


@BOT.message_handler(commands=['anon'])
def anon_message_handler(message):
    """Send anon message to admin place"""
    LOG.log_print("anon_message_handler invoked")
    if message.chat.id > 0:
        if len(message.text) == 5:
            reply(message, "После команды /anon должно следовать то, что надо отправить админам")
        else:
            anon_message(message)
    else:
        reply(message, "Эта команда предназначена для лички")


@BOT.message_handler(commands=['test'])
def database_send_handler(message):
    """ Send all databases to creator """
    LOG.log_print('database_send_handler invoked')
    if message.chat.id == 381279599:
        for file in (DATABASE_FILE, VOTES_FILE, ADAPT_VOTES_FILE, MULTI_VOTES_FILE, SYSTEMS_FILE,
                     STORAGE_FILE):
            file_send = open(file, 'rb')
            send_document(message.chat.id, file_send)
            file_send.close()


# Последний хэндлер. Просто считает сообщения, что не попали в другие хэндлеры


@BOT.message_handler(func=lambda message: True, content_types=all_content_types)
def counter_handler(message):
    """Подсчитывает сообщения"""
    LOG.log_print("counter_handler invoked")
    if in_mf(message, command_type=None, loud=False, or_private=False):
        reactions.trigger(message)
