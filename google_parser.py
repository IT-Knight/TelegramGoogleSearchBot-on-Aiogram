
from aiogram.utils.markdown import quote_html
from bs4 import ResultSet, BeautifulSoup
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


async def google_search(search_query: str, number_of_results=100, language_code="ru") -> list:
    search_text = search_query

    # SearchParams
    # block class for top of position
    # top_position_block = 'ZINbbc xpd O9g5cc uUPGi'
    top_position_block = 'rc'

    def create_instance(index: int, block: ResultSet) -> str:
        # print(block)
        # a = block.find('h3', {'class': "LC20lb DKV0Md"}).text.replace(" ...", "")
        # b = block.find('cite', {'class': ['iUh30', 'Zu0yb', 'tjvcx']}).text
        # c = block.find('a').attrs.get('href')
        # d = block.find('span', {'class': 'aCOpRe'}).text[:170].replace("\n\n", '\n')
        #
        # print(f"""
        # a - {a}
        # b - {b}
        # c - {c}
        # d - {d}
        # """)
        # # print(block)
        # try:
            # d = {'title': block.find('div', {'class': 'BNeawe vvjwJb AP7Wnd'}).text.replace(" ...", ""),
            #      'short_link': block.find('div', {'class': 'BNeawe UPmit AP7Wnd'}).text,
            #      'link': unquote(
            #          re.search(r'((https|http):\/\/[^&]*)', block.find('a').attrs.get('href'))[0]),
            #      'description': block.find('div', {'class': 'BNeawe s3v9rd AP7Wnd'}).text[:170].replace(
            #          "\n\n", '\n')}
        try:
            a = block.find('h3', {'class': "LC20lb DKV0Md"}).text.replace(" ...", "")
        except:
            a = "--no title--"
        try:
            b = block.find('cite', {'class': ['iUh30', 'Zu0yb', 'tjvcx']}).text
        except:
            b = "--no short link--"
        try:
            c = unquote(block.find('a').attrs.get('href'))
        except:
            c = "--no link--"
        try:
            d1 = block.find('span', {'class': 'aCOpRe'}).text[:170].replace("\n\n", '\n')
        except:
            d1 = "--no description--"

        d = {'title': a,
             'short_link': b,
             'link': c,
             'description': d1}
        # print(d)
            # [normalize(d[x]) for x in d.keys()]

        return '{}. {} \n<a href="{}">{}</a>\n {}'.format(index, quote_html(d['title'][:58]), d['link'], d['short_link'].replace(" › ", "/").replace("...", ""), quote_html(d['description']))
        # return ""
        # except:
        #     pass

    search_page_url = f'https://www.google.com/search?q={search_text}&num={number_of_results}&hl={language_code}'
    # headers = {'User-agent': 'Chrome/85.0.4183.102'}
    # response = requests.get(search_page_url, headers=headers)

    chrome_options = Options()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    # driver = webdriver.Chrome()

    driver.get(search_page_url)
    # page_html = response.content.decode('utf-8', errors='ignore')  # type: str
    # print(bool(driver.page_source) is True)
    page_html = driver.page_source  # .decode('utf-8', errors='ignore')  # type: str
    driver.close()
    # with open('1.html', 'w') as ht:
    #     ht.write(page_html)
    soup = BeautifulSoup(page_html, 'html.parser')

    pre_results = soup.find_all('div', {'class': top_position_block})
    # print(len(pre_results))
    # pre_results = list(filter(lambda i: false_position_block in str(i), pre_results))
    # print(type(pre_results))
    # print(all(pre_results))
    results = []

    for block in pre_results:
        res = create_instance(len(results) + 1, block)
        if res:
            results.append(res)

    return results  # , search_page_url)


# if __name__ == "__main__":
#     List = ['1', 'test', 'гугл', 'яндекс', './,:']
#     a = "selenium.common.exeptions.WebDriverException: Message: Can not connect to Service"
#     # for el in List:
#     #     print(google_search(el))
#     [print(x) for x in google_search(a)]