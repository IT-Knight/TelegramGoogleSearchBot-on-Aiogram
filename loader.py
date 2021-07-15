
import logging
from typing import Union, Dict

from aiogram import Bot, Dispatcher, types
from pymongo import MongoClient
import datetime as dt

bot = Bot(token="XXXXXXXXXXXXXXXXXXXXX", parse_mode="HTML")
dp = Dispatcher(bot)


def logging_config():
    format = '%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s'
    logging.basicConfig(format=format, level=logging.INFO)  # level=logging.INFO / DEBUG


class MongoDB:
    MongoClusterLink = "mongodb+srv://ndriuma:atikin@cluster1.dxwlb.mongodb.net/GoogleTelegramBot?retryWrites=true&w=majority"

    def __init__(self):
        self.cluster = MongoClient(self.MongoClusterLink)
        self.db = self.cluster["GoogleTelegramBot"]
        self.check_created_collections(self.db)
        self.collection_logs = self.db["Logs"]
        self.collection_queries = self.db["Queries"]
        self.collection_results = self.db["SearchResults"]

    def check_created_collections(self, db):
        try:
            db.create_collection("Logs")
        except:
            pass
        try:
            db.create_collection("Queries")
        except:
            pass

    def quote_query(self, query: str) -> str:
        forbiden_signs = ['.']
        formated_query = list(query)

        for i, el in enumerate(formated_query):
            if el in forbiden_signs:
                formated_query[i] = "_"
        return "".join(formated_query)

    async def add_search_results(self, search_query: str, results: list):
        search_query = self.quote_query(search_query)

        filter = {search_query: {"$exists": True}}
        results_block = {search_query: results}
        query_update = {search_query: str(dt.datetime.now())}
        self.collection_queries.update(filter, {"$set": query_update}, upsert=True)
        self.collection_results.update(filter, {"$set": results_block}, upsert=True)

    async def getFromDB(self, search_query: str) -> Union[list, bool]:
        search_query = self.quote_query(search_query)
        data = self.collection_results.find({search_query: {"$exists": True}}, {'_id': False})  # type: 'pymongo.cursor.Cursor'
        results_list = list(data)

        # logging.exception("Search query is " + search_query)

        if not results_list:
            return False
        else:
            results = results_list[0].get(search_query)  # type: list
            return results

    async def deleteTable(self):
        inner_querries = self.collection_queries.find({})  # type: list[Dict]
        for query in list(inner_querries):
            query.pop("_id")
            date: str = tuple(query.items())[0][1]  # the str(dt.datetime.now())
            date_obj = dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
            now = dt.datetime.now()
            if date_obj + dt.timedelta(hours=12) < now:
                search_query = tuple(query.items())[0][0]
                delete_filter = {search_query: {"$exists": True}}
                self.collection_results.delete_one(delete_filter)

    async def save_logs(self, post_message: types.Message = None, update=None):
        if post_message:
            data = {"Answer": (dt.datetime.now().strftime("%H:%M:%S [%d-%m-%Y]")) + '\n' + str(post_message)}
            self.collection_logs.insert_one(data)
        if update:
            self.collection_logs.insert_one(update)







