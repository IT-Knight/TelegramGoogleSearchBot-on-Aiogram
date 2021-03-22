
import logging

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types, executor
from loader import logging_config, MongoDB

from datetime import datetime

from handlers import dp


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
                    time_now = datetime.now
                    if len(text) > 8:
                        data1 = {"Update True": f"{time_now().strftime('%H:%M:%S [%d.%m.%Y]')}\n" + str(update) + '\n' + " {}\n".format('-'*65)}
                        await MongoDB().save_logs(update=data1)
                    else:
                        data2 = {"Update False": f"{time_now().strftime('%H:%M:%S [%d.%m.%Y]')}\n" + str(update) + '\n'}
                        await MongoDB().save_logs(update=data2)


async def on_startup(dp):
    dp.middleware.setup(GetDBUpdate())

    # on_startup_notify
    try:
        await dp.bot.send_message("1208151003", "Бот Запущен и готов к работе")
    except Exception as err:
        logging.exception(err)

    # set_default_commands
    await dp.bot.set_my_commands([
        # types.BotCommand("start", "Запустить бота"),
        # types.BotCommand("help", "Помощь"),
        types.BotCommand("google", "/google: <текст поиска>")
    ])


# Обработка измененных сообщений - в разработке
# @dp.edited_message_handler(commands=['google', 'google:'])
# async def message_editor(message: types.Message):
#
#     condition_default = message.text.startswith("/google@TruePython_Bot")
#     condition_google = (message.text.startswith("/google:") or message.text.startswith("/google")) and len(message.text) > 7
#     condition_google2 = message.text.startswith("/google") and len(message.text) <= 7
#     search_text = message.text[8:].strip()
#
#     if condition_default:
#         post_message = await message.edit_text(
#             "<code>Инструкция по использованию:\n/google:[пробел]текст поиска</code>")
#
#     elif condition_google:
#         text = await google_search1(search_text)
#         # отсылаемое сообщение
#         post_message = await message.edit_text(text, disable_web_page_preview=True)
#         # запись post-сообщения
#         with open("GetLogs.txt", 'a', encoding='utf-8') as logFile:
#             logFile.write(str(post_message) + '\n')
#
#     elif condition_google2:
#         post_message = await message.edit_text("Вы не ввели запрос для поиска!")



# logging.basicConfig
logging_config()


executor.start_polling(dp, on_startup=on_startup)


