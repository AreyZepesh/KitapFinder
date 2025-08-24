# import os, sys
# os.chdir( os.path.abspath( os.path.dirname( os.path.dirname(__file__) ) ) )
# sys.path.append( os.getcwd() )

from playwright.async_api import async_playwright, expect
import asyncio
from datetime import datetime

import utils
from models import EBook, ShopCard

async def scroll_to_last(elem_locator, ozon_mode = False):
        """Крутим к последнему элементу, если 5 раз колво не изменилось - далее\n
        ozon_mode ограничевает прокрутку тремя первыми блоками"""
        prev_count = 0
        retries = 0
        max_retries = 5
        ozon_cat_size = 0
        while retries < max_retries:
            count = await elem_locator.count()
            # print("!", len( await elem_locator.evaluate_all("els => els.map(el => el.innerText)") ))
            # print(f"Загружено карточек: {count}") # TODO log
            if count == prev_count:
                retries += 1
            else:
                retries = 0
            prev_count = count

            if ozon_mode:
                if not ozon_cat_size:
                    ozon_cat_size = count
                elif count >= ozon_cat_size*3:
                     break
            
            await elem_locator.nth(count - 1).scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
        # return count

def get_search_urls(base_url, book: EBook) -> list[str]:
    """Генерируем список url для поиска книги, 
    принимает базовый url к которому добавляет данные из объекта книги"""
    search_urls = [(base_url+book.get_search_text(), "text")]
    if book.isbns:
        if book.only_isbn:
             search_urls = []
        search_urls.extend( [(base_url+isbn, "isbn") for isbn in book.isbns] )

    # Затычка сохраняющая ссылки
    for url in search_urls:
        with open(f"./logs/_urls.txt", 'a', encoding="utf8") as file:
            file.write(book.title + " " + url[0] + "\n")
    return search_urls