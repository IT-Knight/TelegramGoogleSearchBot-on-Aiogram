

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from google_search import google_search1
from datetime import datetime

import logging
from database import Database, logger
from config import TOKEN


bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
db = Database()


class Update:

    def __init__(self, update_id='', message='', edited_message='', user_id='', user_name='', message_id='',
                 from_user='', date='', chat='', text='', forward_sender_name='', callback_query=''):

        self.update_id = update_id
        self.message = message  # не dict
        self.edited_message = edited_message  # ? dict?

        self.user_id = user_id  # message.from_user.id
        self.user_name = user_name  # message.from_user.full_name
        self.message_id = message_id
        self.from_user = from_user  # ? dict?
        self.date = date
        self.chat = chat
        self.text = text
        self.forward_sender_name = forward_sender_name
        # inline_query: InlineQuery
        # chosen_inline_result: ChosenInlineResult
        self.callback_query = callback_query


class GetDBUpdate(BaseMiddleware, Update):

    async def on_pre_process_update(self, update: types.Update, data: dict):

        if update.message:
            if update.message.text:
                text = update.message.text
                if text.startswith("/google:") or text.startswith("/google"):
                    with open("GetLogs.txt", 'a', encoding='utf8') as logFile:
                        time_now = datetime.now
                        logFile.write(f"\n{time_now().strftime('%H:%M:%S [%d.%m.%Y]')}\n")
                        if len(text) > 8:
                            logFile.write(str(update) + '\n' + " {}\n".format('-'*65))
                        else:
                            logFile.write(str(update) + '\n')


async def on_startup(dp):
    dp.middleware.setup(GetDBUpdate())

    async def on_startup_notify(dp: Dispatcher):
        try:
            await dp.bot.send_message("1208151003", "Бот Запущен и готов к работе")

        except Exception as err:
            logging.exception(err)

    async def set_default_commands(dp):
        await dp.bot.set_my_commands([
            # types.BotCommand("start", "Запустить бота"),
            # types.BotCommand("help", "Помощь"),
            types.BotCommand("google", "/google: <текст поиска>")
        ])

    await on_startup_notify(dp)
    await set_default_commands(dp)

# Обработка измененных сообщений - в разработке
# @dp.edited_message_handler(commands=['google', 'google:'])
# async def message_editor(message: types.Message):
#
#     condition_default = message.text.startswith("/google@TruePython_Bot")
#     condition_google = (message.text.startswith("/google:") or message.text.startswith("/google")) and len(message.text) > 7
#     condition_google2 = message.text.startswith("/google") and len(message.text) <= 7
#     search_text = message.text[8:].strip()

    # if condition_default:
    #     post_message = await message.edit_text(
    #         "<code>Инструкция по использованию:\n/google:[пробел]текст поиска</code>")
    #
    # elif condition_google:
    #     text = await google_search1(search_text)
    #     # отсылаемое сообщение
    #     post_message = await message.edit_text(text, disable_web_page_preview=True)
    #     # запись post-сообщения
    #     with open("GetLogs.txt", 'a', encoding='utf-8') as logFile:
    #         logFile.write(str(post_message) + '\n')
    #
    # elif condition_google2:
    #     post_message = await message.edit_text("Вы не ввели запрос для поиска!")


@dp.message_handler(commands=['google', 'google:'])
async def sender(message: types.Message):

    print(message)    
    condition_default = message.text.startswith("/google@TruePython_Bot")

    condition_google = (message.text.startswith("/google:") or message.text.startswith("/google")) and len(message.text) > 7

    condition_google2 = message.text.startswith("/google") and len(message.text) <= 7
    search_text = message.text[8:].strip()
    print(search_text)
    # Не Удаляются запросы старше 12 часов
    db.deleteTable()
    if condition_default:
        post_message = await message.answer("<code>Инструкция по использованию:\n/google:[пробел]текст поиска</code>", reply=True)

    elif condition_google2:
        post_message = await message.answer("Вы не ввели запрос для поиска!", reply=True)

    elif condition_google:

        try:
            results: list = db.getFromDB(search_text)
        except:
            results: list = await google_search1(search_text)
            # результаты поиска заносяться в БД
            db.add_search_results(search_text, results)

        text = "\n".join(results[:4])
        print(text)
        keyboard = InlineKeyboardMarkup(row_width=2,
                                        inline_keyboard=[[InlineKeyboardButton(text="Next", callback_data="Next|0|4")]])
                                                # , [InlineKeyboardButton(text="Go to Search Page",url=search_page)]])

        # отсылаемое сообщение
        post_message = await message.answer(text, disable_web_page_preview=True, reply=True, reply_markup=keyboard)
        # запись post-сообщения
        with open("GetLogs.txt", 'a', encoding='utf-8') as logFile:
            logFile.write(str(post_message)+'\n')








@dp.callback_query_handler()
async def callback_proccess(callback_query: types.CallbackQuery):
    callback_data = callback_query.data  # type: str
    print(callback_data)
    list3 = callback_data.split("|")  # type: list
    print(list3)
    option = list3[0]  # type: str
    start = int(list3[1])  # type: int
    end = int(list3[2])  # type: int
    print(option, start, end)

    search_text = callback_query.message.reply_to_message.text[8:].strip()
    print(search_text)
    # достаем из БД результаты поиска!
    text_list: list = db.getFromDB(search_text)

    if option == "Next":
        start += 4
        end += 4
    elif option == "Back":
        start -= 4
        end -= 4
    print(start, end)
    keyboard = None
    if 3 < start < 96:
        keyboard = InlineKeyboardMarkup(row_width=2,
                                        inline_keyboard=[[InlineKeyboardButton(text="Back", callback_data=f"Back|{start}|{end}"),
                                                          InlineKeyboardButton(text="Next", callback_data=f"Next|{start}|{end}")]])
    elif start <= 3:
        keyboard = InlineKeyboardMarkup(row_width=1,
                                        inline_keyboard=[[InlineKeyboardButton(text="Next", callback_data=f"Next|{start}|{end}")]])
    elif start >= 96:
        keyboard = InlineKeyboardMarkup(row_width=1,
                                        inline_keyboard=[[InlineKeyboardButton(text="Back", callback_data=f"Back|{start}|{end}")]])

    text: str = "\n".join(text_list[start:end])
    await callback_query.message.edit_text(text, disable_web_page_preview=True, reply_markup=keyboard)

    # option = callback_query.data
    # chat_id = callback_query.message.chat.id
    # message_id_to_edit = callback_query.message.message_id

# logging.basicConfig
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                     level=logging.INFO,
                     # level=logging.DEBUG,
                     )

# error handler
@dp.errors_handler()
async def errors_handler(update, exception):
    """
    Exceptions handler. Catches all exceptions within task factory tasks.
    :param dispatcher:
    :param update:
    :param exception:
    :return: stdout logging
    """
    from aiogram.utils.exceptions import (Unauthorized, InvalidQueryID, TelegramAPIError,
                                          CantDemoteChatCreator, MessageNotModified, MessageToDeleteNotFound,
                                          MessageTextIsEmpty, RetryAfter,
                                          CantParseEntities, MessageCantBeDeleted)

    if isinstance(exception, CantDemoteChatCreator):
        logging.debug("Can't demote chat creator")
        return True

    if isinstance(exception, MessageNotModified):
        logging.debug('Message is not modified')
        return True
    if isinstance(exception, MessageCantBeDeleted):
        logging.debug('Message cant be deleted')
        return True

    if isinstance(exception, MessageToDeleteNotFound):
        logging.debug('Message to delete not found')
        return True

    if isinstance(exception, MessageTextIsEmpty):
        logging.debug('MessageTextIsEmpty')
        return True

    if isinstance(exception, Unauthorized):
        logging.info(f'Unauthorized: {exception}')
        return True

    if isinstance(exception, InvalidQueryID):
        logging.exception(f'InvalidQueryID: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, TelegramAPIError):
        logging.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, RetryAfter):
        logging.exception(f'RetryAfter: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, CantParseEntities):
        logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
        return True
    logging.exception(f'Update: {update} \n{exception}')

executor.start_polling(dp, on_startup=on_startup)


