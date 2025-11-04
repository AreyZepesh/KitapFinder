# import os, sys
# os.chdir( os.path.abspath( os.path.dirname( os.path.dirname(__file__) ) ) )
# sys.path.append( os.getcwd() )

from playwright.async_api import async_playwright, expect
import asyncio
from datetime import datetime as dt
from tqdm.asyncio import tqdm
from functools import wraps
import traceback
import contextvars

import utils
from models import EBook, ShopCard, ParserConfig

ERROR_PREFIX = contextvars.ContextVar("Ошибка")
LOG_URL = contextvars.ContextVar("")

def try_and_log_decor(header: str, repeats: int = 1):
    """Асинхронный декоратор с повтором и логированием ошибок."""
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            for trys in range(repeats):
                try:
                   return await fn(*args, **kwargs)
                except Exception as ex:
                    base_out = "\n".join([
                            f"{dt.now().strftime("%Y-%m-%d %H-%M-%S")}",
                            ERROR_PREFIX.get(),
                            f"{header} ({trys+1}/{repeats})"
                            ])
                    tqdm.write(f"{base_out}")
                    tqdm.write(f"{ex}")
                    with open(f"./logs/_error.txt", 'a', encoding="utf8") as error_file:
                        error_file.write(base_out+"\n")
                        error_file.write(LOG_URL.get() + "\n")
                        error_file.write(f"{fn.__name__}\n")
                        error_file.write(f"{traceback.format_exc()}\n")
                        error_file.write(f"{ex}\n")
                        error_file.write("\n")

        return wrapper
    return decorator

async def scroll_to_last(elem_locator, strore = None):
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

            if strore == "ozon":
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
    search_urls = [(str(base_url+book.get_search_text()).replace(" ", "+"), "text")]
    if book.isbns:
        if book.only_isbn:
             search_urls = []
        search_urls.extend( [(base_url.replace(" ", "+")+isbn, "isbn") for isbn in book.isbns] )

    # Затычка сохраняющая ссылки
    for url in search_urls:
        with open(f"./logs/_urls.txt", 'a', encoding="utf8") as file:
            file.write(book.title + " " + url[0] + "\n")
    return search_urls

async def image_from_response(response):
    content_type = response.headers.get("content-type", "").lower()

    if not content_type.startswith("image/"):
        # Можно логировать или сохранять ошибку
        return None

    # Проверяем статус
    if not response.ok:
        return None
    
    return await response.body()

@try_and_log_decor("Переход на страницу")
async def goto_url(page, url):
    # # один день была ошибка, с flip типо страница не загрузилась, тестируем обход:
    # try:
    #     await page.goto(url[0])
    # except Exception as ex1:
    #     tqdm.write(ERROR_PREFIX.get())
    #     tqdm.write(f"{ex1}")
    #     tqdm.write("Ошибка при попытке загрузить страницу, пытаемся, ожидая domcontentloaded")
    #     try:
    #         await page.goto(url[0], wait_until="domcontentloaded")
    #     except Exception as ex2:
    #         tqdm.write(f"{ex2}")
    #         tqdm.write("Ошибка при попытке загрузить страницу, пытаемся, ожидая commit")
    #         try:
    #             await page.goto(url[0], wait_until="commit")
    #         except Exception as ex3:
    #             tqdm.write(f"{ex3}")
    #             tqdm.write(f"Ваще пипец, вырубаем)")
    #             raise ex3

    #     finally:
    #         tqdm.write(f"{'='*50}")
    await page.goto(url)

@try_and_log_decor("Обработка одной карточки")
async def wait_page(page, parser_config):
    await page.wait_for_load_state(parser_config.wait_for_load_stat)
    await page.wait_for_timeout(parser_config.wait_for_load_time)

@try_and_log_decor("Обработка одной карточки", repeats=3)
async def parse_card(page, card, book, parser_config):
    card_title = await parser_config.get_card_title(card)
    if book.is_TITLE_in_STR(card_title):
        price = utils.normalizePrice( await parser_config.get_card_price(card) )
        article = await parser_config.get_card_article(card)
        screen_file = f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}/{book.title.replace(":","")}/{parser_config.store}_{price}_{article}.png"
        cover_bytes = await image_from_response( await parser_config.get_card_cover(card, page) )
        card_info = await parser_config.get_card_screen(card)
        screen_bytes = await card_info.screenshot(
            # path=screen_file.replace(".png", "_card.png")
            ) #TODO screen
        await card.screenshot(path=screen_file)
        return ShopCard(
            price = price, 
            store = parser_config.store, 
            article = article, 
            screen_file = screen_file, 
            cover_bytes = cover_bytes,
            screen_bytes = screen_bytes #TODO photo
            )
    pass

@try_and_log_decor("Парсим данные: основная функция")
async def run_parser(context, book: EBook, parser_config: ParserConfig) ->  list[ShopCard]:
    """Парсер, принимает контекст и объект книги, возвращает список объектов с 'карточками'"""
    page = await context.new_page()
    all_items = []
    search_urls = get_search_urls(parser_config.base_url, book)
    ERROR_PREFIX.set(f"{book.title}: {parser_config.store}")
    for url in search_urls:
        LOG_URL.set(url[0])
        await goto_url(page, url[0])

        await wait_page(page, parser_config)
        
        await parser_config.fn_extra_goto(page)

        if await parser_config.fn_noresults(page):
            # tqdm.write("!пропуск итерации - нет результатов")
            # await page.screenshot(path=f"./logs/_nores/{dt.now().strftime("%Y-%m-%d-%H-%M")}__{book.title.replace(":","")}__{parser_config.store}.png")
            # nores screen - адрес формировать заранее и передовать в функцию?
            continue

        # проверяем и переключаем валюту
        fn_currency = parser_config.fn_currency
        await fn_currency(page)

        # указываем адрес
        await parser_config.fn_city(page)

        # Парсим карточки товаров, сперва получаем "каталог"
        cat = parser_config.get_cat_locator(page)
        # Ищем последний элемент на странице, 
        await scroll_to_last(cat, strore=parser_config.store)

        # Каталог прогружен, получаем все элементы и обходим по одному,
        # что по названию не подходит - пропускаем
        cat = await cat.all()
        await parser_config.fn_extra_wait_cat(page)

        for card in cat:
            result = await parse_card(page, card, book, parser_config)
            if result:
                result.type_search = url[-1]
                all_items.append(result)

    await page.close()
    return all_items
