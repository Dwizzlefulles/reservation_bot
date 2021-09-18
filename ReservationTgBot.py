from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, Handler
import datetime
import re
import json
from os import path


# прописываем стартовую команду
def start(update, context):
    first_name = update.message.chat.first_name
    update.message.reply_text(f"Hi {first_name}, чтобы узнать команды бота напиши /help !")


# остановка если юзер накосячил
def stop(update, context):
    update.message.reply_text('Остановочка!')
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text('Привет я своего рода секретарь:) Я умею выдавать забронированные даты'
                              ' и регестрировать бронь. Чтобы узнать уже забронированные даты напиши /check, '
                              'чтобы сделать бронь напиши /reg. Напиши /stop , чтобы закончить работу. Чтобы отменить '
                              'свою бронь введите /del')


# we r checking for reserved dates
def check(update, context):
    datetoday = datetime.date.today()
    tomorrow = datetoday + datetime.timedelta(days=1)
    # checking for first load, if load is first we r going into except
    try:
        with open('storage.json', 'r', encoding='utf-8') as f:
            reserved = json.load(f)
            update.message.reply_text(f'Занятые часы на сегодня')
            for key in reserved:
                strcheckdate1 = reserved[key]["datereg"]
                readycheckdate1 = datetime.date(*map(int, strcheckdate1.split('-')))
                if datetoday == readycheckdate1:
                    update.message.reply_text(f'С {reserved[key]["starttime"]}  по {reserved[key]["finishtime"]} '
                                              f'назначено {reserved[key]["selectedevent"]}  '
                                              f'юзером {reserved[key]["whois"]}')
            update.message.reply_text(f'Занятые часы на завтра')
            for key in reserved:
                strcheckdate1 = reserved[key]["datereg"]
                readycheckdate1 = datetime.date(*map(int, strcheckdate1.split('-')))
                if tomorrow == readycheckdate1:
                    update.message.reply_text(f'С {reserved[key]["starttime"]}  по {reserved[key]["finishtime"]} '
                                              f'назначено {reserved[key]["selectedevent"]} '
                                              f'юзером {reserved[key]["whois"]}')
    except FileNotFoundError:
        update.message.reply_text(f'К счастью все места свободны!!!')


def error(update, context):
    update.message.reply_text('Дурачок разработчик(или не разработчик:) ), допустил ошибку. Обратитесь в тп')


def reg_event_start(update, context):
    update.message.reply_text('Привет, далее будет регистрация вашего ивента. Напиши мне как будешь готов')
    return 1


def reg_event_cont(update, context):
    update.message.reply_text('Назовите событие, которое вы хотите назначить')
    return 2


def reg_end(update, context):
    global selectedevent
    selectedevent = update.message.text
    update.message.reply_text('Вы хотите зарезервировать время на сегодня или на завтра?')
    return 3


def selectday(update, context):
    global selectedday
    selectedday = update.message.text
    if selectedday == 'сегодня' or selectedday == 'Сегодня' or selectedday == 'завтра' or selectedday == 'Завтра':
        update.message.reply_text('Выберите время начала в формате hh:mm с 09:00 до 21:00')
        return 4
    else:
        update.message.reply_text('Кажется кто-то допустил грамматическую ошибку :) Попробуем еще раз?'
                                  '(напиши чтобы продолжить)')
        return 2


def selectfirsttime(update, context):
    global starth
    global time1
    datetoday = datetime.date.today()
    tomorrow = datetoday + datetime.timedelta(days=1)
    time1 = update.message.text
    if re.match(r"\d\d:\d\d", time1):
        hours1 = time1.split(':')
        try:
            starth = datetime.time(int(hours1[0]), int(hours1[1]))
        except ValueError:
            update.message.reply_text('Неправильный формат времени. Напишите, чтобы продолжить!!!')
            return 2
        if starth > datetime.time(21, 00) or starth < datetime.time(9, 00):
            update.message.reply_text('Неправильный формат времени. Напишите, чтобы продолжить!')
            return 2
        else:
            try:
                with open('storage.json', 'r', encoding='utf-8') as f:
                    reserved = json.load(f)
                if selectedday == 'сегодня' or selectedday == 'Сегодня':
                    datereg = str(datetoday)
                else:
                    datereg = str(tomorrow)
                for key in reserved:
                    value = reserved[key]["datereg"]
                    if value == datereg:
                        strchecktime1 = reserved[key]["starttime"]
                        readychecktime1 = datetime.time(*map(int, strchecktime1.split(':')))
                        strchecktime2 = reserved[key]["finishtime"]
                        readychecktime2 = datetime.time(*map(int, strchecktime2.split(':')))
                        if (starth >= readychecktime1) and (starth <= readychecktime2):
                            update.message.reply_text(
                                'Это время уже занято. Напишите, чтобы пройти регистрацию')
                            return 2
                else:
                    update.message.reply_text('Выберите время окончания в формате hh:mm с 09:00 до 21:00')
                    return 5
            except FileNotFoundError:
                update.message.reply_text('Выберите время окончания в формате hh:mm с 09:00 до 21:00')
                return 5
    else:
        update.message.reply_text('Неправильный формат времени. Напишите, чтобы продолжить')
        return 2


def selectsecondtime(update, context):
    global endh
    time2 = update.message.text
    first_name = update.message.chat.first_name
    datetoday = datetime.date.today()
    tomorrow = datetoday + datetime.timedelta(days=1)
    unique = 0
    if selectedday == 'сегодня' or selectedday == 'Сегодня':
        datetoday = str(datetime.date.today())
    else:
        datetoday = str((datetoday + datetime.timedelta(days=1)))
    if re.match(r"\d\d:\d\d", time2):
        hours2 = time2.split(':')
        try:
            endh = datetime.time(int(hours2[0]), int(hours2[1]))
        except ValueError:
            update.message.reply_text('Неправильный формат времени. Напишите, чтобы продолжить')
            return 2
        if endh > datetime.time(21, 00) or endh < datetime.time(9, 00):
            update.message.reply_text('Неправильный формат времени. Напишите, чтобы продолжить')
            return 2
        else:
            if endh > starth:
                try:
                    with open('storage.json', 'r', encoding='utf-8') as f:
                        reserved = json.load(f)
                    if selectedday == 'сегодня' or selectedday == 'Сегодня':
                        datereg = str(datetoday)
                    else:
                        datereg = str(tomorrow)
                    for key in reserved:
                        value = reserved[key]["datereg"]
                        if value == datereg:
                            strchecktime1 = reserved[key]["starttime"]
                            readychecktime1 = datetime.time(*map(int, strchecktime1.split(':')))
                            strchecktime2 = reserved[key]["finishtime"]
                            readychecktime2 = datetime.time(*map(int, strchecktime2.split(':')))
                            if (endh >= readychecktime1) and (endh <= readychecktime2):
                                update.message.reply_text(
                                    'Это время уже занято. Напишите, чтобы пройти регистрацию')
                                return 2
                except FileNotFoundError:
                    print('привет тому, кто читает этот код:)')
                # if there's no json file programm will create it
                if path.isfile("storage.json"):
                    with open("storage.json", "r", encoding="utf8") as f:
                        storage = json.load(f)
                else:
                    storage = {}
                try:
                    k = list(storage.keys())
                    unique = int(k[-1]) + 1
                except IndexError:
                    unique = 0
                finally:
                    storage[unique] = {'starttime': time1, 'finishtime': time2,
                                       'selectedevent': selectedevent, 'whois': first_name,
                                       'datereg': datetoday}
                    # дампим в жсон ничего необычного
                    with open("storage.json", "w", encoding="utf8") as f:
                        json.dump(storage, f, indent=4, ensure_ascii=False)
            else:
                update.message.reply_text('Кажется вы что-то перепутали :) Напишите мне, чтобы продолжить')
                return 2
    else:
        update.message.reply_text('Неправильный формат времени. Напишите, чтобы продолжить')
        return 2
    update.message.reply_text('Хорошо,данные приняты')
    return ConversationHandler.END


def delreqstart(update, context):
    try:
        with open('storage.json', 'r', encoding='utf-8') as f:
            update.message.reply_text(
                'Введите название события, которое вы хотите удалить из брони.(возможно удалять,'
                'только свои события)')
        return 1
    except FileNotFoundError:
        update.text.message.reply_text('Еще не было зарегистрировано ни одного события')
        return ConversationHandler.END


def eventname(update, context):
    global searchevent
    searchevent = update.message.text
    update.message.reply_text('Введите дату, на которую была оформлена бронь в формате YYYY-MM-DD')
    return 2


def datename(update, context):
    global searchdate
    searchdate = update.message.text
    if re.match(r"\d\d\d\d-\d\d-\d\d", searchdate):
        update.message.reply_text('Введите дату начала события, которое вы хотите отменить в формате hh:mm')
        return 3
    else:
        update.message.reply_text('2Кажется вы допустили ошибку при ввроде даты. Напишите чтобы начать заново')
        return 1


def starttimeevent(update, context):
    global searchtime1
    searchtime1 = update.message.text
    if re.match(r"\d\d:\d\d", searchtime1):
        update.message.reply_text('Введите дату окончания события, которое вы хотите отменить в формате hh:mm')
        return 4
    else:
        update.message.reply_text('Кажется вы допустили ошибку при ввроде времени. Напишите чтобы начать заново')
        return 1


# final stage of removing event
def endttimeevent(update, context):
    searchtime2 = update.message.text
    first_name = update.message.chat.first_name
    if re.match(r"\d\d:\d\d", searchtime2):
        with open('storage.json', 'r', encoding='utf-8') as f:
            reserved = json.load(f)
        for key in reserved:
            if (reserved[key]["starttime"] == searchtime1) and (reserved[key]["finishtime"] == searchtime2) \
                    and (reserved[key]["whois"] == first_name) and (reserved[key]["selectedevent"]) == searchevent:
                del reserved[key]
                break
        with open("storage.json", "w", encoding="utf8") as f:
            json.dump(reserved, f, indent=4, ensure_ascii=False)
        update.message.reply_text('Удаление прошло успешно!')
        return ConversationHandler.END

    else:
        update.message.reply_text('6Кажется вы допустили ошибку при вводе времени. Напишите чтобы начать заново')
        return 1


# как сделать многопоток????))))
# def chekingdate():
# with open('storage.json', 'r', encoding='utf-8') as f:
#     reserved = json.load(f)
# starttimecount = datetime.time()
# currentday = datetime.datetime.now(tz=None)
# nextday = (currentday + datetime.timedelta(days=1))
# print(nextday)
# while True:
#     time.sleep(2.0 - ((datetime.time() - starttimecount) % 2.0))
#     print('123')
#     if currentday == nextday:
#         for key in reserved:
#             if reserved[key]["day"] == "завтра":
#                 reserved[key]['day'] = reserved[key]["сегодня"]
#             else:
#                 del reserved[key]
#     nextday = (nextday + datetime.timedelta(days=1))


def main():
    token = ""

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # making handler for consistently dialogue
    conv_handlerreg = ConversationHandler(
        entry_points=[CommandHandler('reg', reg_event_start)],
        states={
            1: [
                MessageHandler(Filters.text, reg_event_cont)
            ],
            2: [
                MessageHandler(Filters.text, reg_end)
            ],
            3: [
                MessageHandler(Filters.text, selectday)
            ],
            4: [
                MessageHandler(Filters.text, selectfirsttime)
            ],
            5: [
                MessageHandler(Filters.text, selectsecondtime)
            ],
        },
        fallbacks=[
            CommandHandler('stop', stop)
        ]
    )

    conv_handlerdel = ConversationHandler(
        entry_points=[CommandHandler('del', delreqstart)],
        states={
            1: [
                MessageHandler(Filters.text, eventname)
            ],
            2: [
                MessageHandler(Filters.text, datename)
            ],
            3: [
                MessageHandler(Filters.text, starttimeevent)
            ],
            4: [
                MessageHandler(Filters.text, endttimeevent)
            ],
        },
        fallbacks=[
            CommandHandler('stop', stop)
        ]
    )

    # тут хендлеры для команд, не связанных с conv_handler
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("check", check))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("first", selectfirsttime))
    dp.add_handler(conv_handlerreg)
    dp.add_handler(conv_handlerdel)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
