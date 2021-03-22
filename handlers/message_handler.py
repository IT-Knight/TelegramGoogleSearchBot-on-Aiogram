
import logging
from typing import Union

from loader import dp, types, MongoDB
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from google_parser import google_search


@dp.message_handler(commands=['google', 'google:'])
async def sender(message: types.Message):

    print(message)
    condition_default = message.text.startswith("/google@TruePython_Bot")

    condition_google = (message.text.startswith("/google:") or message.text.startswith("/google")) and len(message.text) > 7

    condition_google2 = message.text.startswith("/google") and len(message.text) <= 7
    search_text: str = message.text[8:].strip()
    print(search_text)
    # Удаляются запросы старше 12 часов
    await MongoDB().deleteTable()
    if condition_default:
        post_message = await message.answer("<code>Инструкция по использованию:\n/google: текст поиска</code>", reply=True)

    elif condition_google2:
        post_message = await message.answer("Вы не ввели запрос для поиска!", reply=True)

    elif condition_google:
        results: Union[list, bool] = await MongoDB().getFromDB(search_text)
        if not results:
            results: list = await google_search(search_text)
            # результаты поиска заносяться в БД
            await MongoDB().add_search_results(search_text, results)

        text = "\n".join(results[:4])
        print(text)
        keyboard = InlineKeyboardMarkup(row_width=2,
                                        inline_keyboard=[[InlineKeyboardButton(text="Next", callback_data="Next|0|4")]])
                                                # , [InlineKeyboardButton(text="Go to Search Page",url=search_page)]])

        # отсылаемое сообщение
        post_message = await message.answer(text, disable_web_page_preview=True, reply=True, reply_markup=keyboard)
        # запись post-сообщения
        await MongoDB().save_logs(post_message=post_message)
