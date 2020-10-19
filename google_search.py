
from aiogram.utils.markdown import quote_html
from bs4 import ResultSet, BeautifulSoup
from urllib.parse import unquote
import requests
import re


async def google_search1(search_query: str, number_of_results=100, language_code="ru") -> list:
    search_text = search_query

    # SearchParams
    # block class for top of position
    top_position_block = 'ZINbbc xpd O9g5cc uUPGi'
    # filtered class, for false position
    false_position_block = 'BNeawe vvjwJb AP7Wnd'
    true_description_block = 'BNeawe s3v9rd AP7Wnd'

    def create_instance(index: int, block: ResultSet) -> str:
        try:
            d = {'title': block.find('div', {'class': 'BNeawe vvjwJb AP7Wnd'}).text.replace(" ...", ""),
                 'short_link': block.find('div', {'class': 'BNeawe UPmit AP7Wnd'}).text,
                 'link': unquote(
                     re.search(r'((https|http):\/\/[^&]*)', block.find('a').attrs.get('href'))[0]),
                 'description': block.find('div', {'class': 'BNeawe s3v9rd AP7Wnd'}).text[:170].replace(
                     "\n\n", '\n')}

            # [normalize(d[x]) for x in d.keys()]

           # return '{}. {}</a> \n <code>{}</code> \n {}'.format(index, d['link'], d['title'], d['short_link'], d['description'])

            return '{}. {} \n<a href="{}">{}</a>\n {}'.format(index, quote_html(d['title'][:58]), d['link'], d['short_link'].replace(" › ", "/").replace("...", ""), quote_html(d['description']))
        except:
            pass

    search_page_url = f'https://www.google.com/search?q={search_text}&num={number_of_results}&hl={language_code}'
    headers = {'User-agent': 'Chrome/85.0.4183.102'}
    response = requests.get(search_page_url, headers=headers)

    page_html = response.content.decode('utf-8', errors='ignore')  # type: str
    # with open('1.html', 'w') as ht:
    #     ht.write(page_html)
    soup = BeautifulSoup(page_html, 'html.parser')

    pre_results = soup.find_all('div', {'class': top_position_block})

    pre_results = list(filter(lambda i: false_position_block in str(i), pre_results))

    results = []
    for pre_result in pre_results:
        res = create_instance(len(results) + 1, pre_result)
        if res:
            results.append(res)
    return results  #, search_page_url)

if __name__ == "__main__":
    google_search1("как измерить сколько весит текст в байтах python")