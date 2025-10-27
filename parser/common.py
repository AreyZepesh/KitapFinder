# import os, sys
# os.chdir( os.path.abspath( os.path.dirname( os.path.dirname(__file__) ) ) )
# sys.path.append( os.getcwd() )

from playwright.async_api import async_playwright, expect
import asyncio
from datetime import datetime as dt
from tqdm.asyncio import tqdm

import utils
from models import EBook, ShopCard, ParserConfig


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

async def run_parser(context, book: EBook, parser_config: ParserConfig) ->  list[ShopCard]:
    """Парсер, принимает контекст и объект книги, возвращает список объектов с 'карточками'"""
    error_prefix = f"\n{book.title} {parser_config.store}:"
    all_items = []
    search_urls = get_search_urls(parser_config.base_url, book)

    page = await context.new_page()

    for url in search_urls:
        try:
            # # один день была ошибка, с flip типо страница не загрузилась, тестируем обход:
            # try:
            #     await page.goto(url[0])
            # except Exception as ex1:
            #     tqdm.write(error_prefix)
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
            await page.goto(url[0])
            try:
                await page.wait_for_load_state(parser_config.wait_for_load_stat)
                await page.wait_for_timeout(parser_config.wait_for_load_time)
            except Exception as ex:
                tqdm.write(error_prefix)
                tqdm.write("wait load page:")
                tqdm.write(f"{ex}")
            
            await parser_config.fn_extra_goto(page)

            if await parser_config.fn_noresults(page):
                # tqdm.write("!пропуск итерации - нет результатов")
                await page.screenshot(path=f"./logs/_nores/{dt.now().strftime("%Y-%m-%d-%H-%M")}__{book.title.replace(":","")}__{parser_config.store}.png")
                # nores screen - адрес формировать заранее и передовать в функцию?
                continue

            # проверяем и переключаем валюту
            fn_currency = parser_config.fn_currency
            await fn_currency(page, error_prefix)

            # указываем адрес
            await parser_config.fn_city(page, error_prefix)

            # Парсим карточки товаров, сперва получаем "каталог"
            cat = parser_config.get_cat_locator(page)
            # Ищем последний элемент на странице, 
            await scroll_to_last(cat, strore=parser_config.store)
 
            # Каталог прогружен, получаем все элементы и обходим по одному,
            # что по названию не подходит - пропускаем
            cat = await cat.all()
            await parser_config.fn_extra_wait_cat(page)

            for card in cat:
                # TODO ретраить при ошибке?
                try:
                    card_title = await parser_config.get_card_title(card)
                    if book.is_TITLE_in_STR(card_title):
                        price = utils.normalizePrice( await parser_config.get_card_price(card) )
                        article = await parser_config.get_card_article(card)
                        screen_file = f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}/{book.title.replace(":","")}/{parser_config.store}_{price}_{article}.png"
                        photo_b = await image_from_response( await parser_config.get_card_photo(card, page) ) #TODO photo
                        all_items.append(ShopCard(
                            price=price, 
                            store=parser_config.store, 
                            article=article, 
                            screen_file=screen_file, 
                            type_search=url[-1],
                            cover_bytes = photo_b #TODO photo
                            ))
                        await card.screenshot(path=screen_file)
                        # TODO Убрать коммент скриншота
                except Exception as ex:
                    # import traceback
                    # error_text = traceback.format_exc()
                    tqdm.write(error_prefix)
                    tqdm.write("Ошибка при обработке одной карточки:")
                    tqdm.write(f"{ex}")
                    # tqdm.write(f"{error_text}")
                    # input()


        except Exception as ex:
            import traceback
            error_text = traceback.format_exc()
            with open(f"./logs/_error.txt", 'a', encoding="utf8") as file:
                file.write(url[0]+"\n")
                file.write(f"{error_text}\n")
                file.write(f"{ex}\n\n")
            tqdm.write(error_prefix)
            # tqdm.write(f"{error_text}")
            tqdm.write(f"{ex}")
            # tqdm.write(f"{parser_config}")
            # raise ex
            # input("!!!!!!!!!!!!!!!!!!!!!")

    # TODO del
    # x = input("send anything") 

    await page.close()
    return all_items
