import sqlite3
import datetime as dt


class Database:
    path_to_db = "results_saver.db"

    def __init__(self):
        self.connection = sqlite3.connect(self.path_to_db)

    def execute(self, sql_query: str, parameters: tuple = tuple(), fetchone=False, fetchall=False, commit=True):

        cursor = self.connection.cursor()
        print(sql_query)
        cursor.execute(sql_query, parameters)

        data = None
        # self.connection.set_trace_callback(logger)
        # if commit:
        #     self.connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()


        return data

    def quote_query(self, query):
        formated_query = query.replace(" ", "_").replace("__", "_")
        return formated_query

    def add_search_results(self, search_query: str, results: list):
        self.connection = sqlite3.connect(self.path_to_db)
        search_query = self.quote_query(search_query)
        with open("QueriesInDB.txt", "a", encoding="utf-8") as qdb:
            qdb.write(f"{search_query}+" + str(dt.datetime.now()) + "\n")

        sql = f'CREATE TABLE IF NOT EXISTS {search_query} (results TEXT)'
        print(sql)
        self.execute(sql_query=sql)
        for value in results:
            self.execute('INSERT INTO {}(results) VALUES (?)'.format(search_query), parameters=(value,))
        self.connection.commit()
        self.connection.close()

    def getFromDB(self, search_query: str) -> list:
        self.connection = sqlite3.connect(self.path_to_db)
        search_query = self.quote_query(search_query)
        sql = f"SELECT results FROM {search_query}"
        print(sql)
        google_results_list = [x[0] for x in self.execute(sql, fetchall=True)]
        self.connection.close()
        return google_results_list

    def deleteTable(self, search_query: str=None):
        try:
            self.connection = sqlite3.connect(self.path_to_db)
            with open("QueriesInDB.txt", "r", encoding="utf-8") as qdb:
                for el in qdb.readlines():
                    data = el.strip("\n").split("+")
                    # print(data)
                    date = data[1]
                    # print(date)
                    date = dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                    now = dt.datetime.now()
                    if date + dt.timedelta(hours=12) < now:
                        sql = f"DROP TABLE {data[0]}"
                        self.execute(sql)
                self.connection.commit()
                self.connection.close()
        except:
            pass



def logger(statement):
    print(f"""    ________________________________________________________________________
    Executing:
    {statement}
    ________________________________________________________________________""")


# Database().add_search_results("ps4", [1, 2, 3, 4, 5, 6, 10, 20, 30])
# Database().getFromDB("ps3")
# Database.add_search_results(search_query, results_list)

