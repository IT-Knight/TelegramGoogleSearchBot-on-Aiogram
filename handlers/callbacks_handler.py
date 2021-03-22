
from loader import dp, types, MongoDB
from google_parser import google_search

InlineKeyboardMarkup = types.InlineKeyboardMarkup
InlineKeyboardButton = types.InlineKeyboardButton


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
    text_list: list = await MongoDB().getFromDB(search_text)

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

    if text_list:
        text: str = "\n".join(text_list[start:end])
        await callback_query.message.edit_text(text, disable_web_page_preview=True, reply_markup=keyboard)
    else:
        results: list = await google_search(search_text)

        text = "\n".join(results[:4])

        await MongoDB().add_search_results(search_text, results)

        keyboard = InlineKeyboardMarkup(row_width=2,
                                        inline_keyboard=[[InlineKeyboardButton(text="Next", callback_data="Next|0|4")]])
        print("Callback Else: rewrite in Mongo")
        post_message = await callback_query.message.edit_text(text, disable_web_page_preview=True, reply_markup=keyboard)

        await MongoDB().save_logs(post_message=post_message)

