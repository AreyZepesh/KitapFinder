# import os, sys
# os.chdir( os.path.abspath( os.path.dirname( os.path.dirname(__file__) ) ) )
# sys.path.append( os.getcwd() )

from patchright.async_api import (
# from playwright.async_api import (
    async_playwright, expect, 
    Page, BrowserContext, Locator, APIResponse,
    TimeoutError)
import asyncio
from datetime import datetime as dt
from tqdm.asyncio import tqdm
from functools import wraps
import traceback
import contextvars
import re, sys, random

import utils
from models import EBook, ShopCard, ParserConfig

ERROR_PREFIX = contextvars.ContextVar("Ошибка")
LOG_URL = contextvars.ContextVar("")
CURRENT_PAGE = contextvars.ContextVar("")

async def screen_and_save_page(dir_path: str, page: Page, file_prefix: str = "", file_suffix: str = ""):
    while dir_path[-1] == "/":
        dir_path = dir_path[:-1]
    base_path = f"{dir_path}/{file_prefix}{dt.now().strftime("%Y-%m-%d %H-%M-%S")}{file_suffix}"
    await page.screenshot(path=f"{base_path}.png")
    with open(f"{base_path}.html", "w", encoding="utf-8-sig") as f:
        f.write(utils.prettify_html(await page.content()))

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
                        
                        if trys+1 == repeats: # выводить ошибку только если она провалила последнюю попытку
                        # if sys.platform == "linux":
                            # при ошибке - скриншот и сохранение кода страницы
                            page: Page = CURRENT_PAGE.get()
                            await screen_and_save_page(dir_path = './logs/err', page = page)

                            # tqdm.write(f"{ex}")
                            # # для patchright
                            try:
                                # tb_lines = traceback.format_exception(type(ex), ex, ex.__traceback__)
                                tb_lines = str(ex).split("\n")
                                if len(tb_lines) > 10:
                                    short_tb = (
                                        tb_lines[:5] +
                                        ["\n...\n"] +
                                        tb_lines[-5:]
                                    )
                                    tqdm.write("".join(short_tb))
                                else:
                                    tqdm.write("".join(tb_lines))
                            except Exception as path_ex:
                                tqdm.write(f"{ex}")
                                tqdm.write(f"\n... и ошибка сокращения ошибки)))")
                                tqdm.write(f"{path_ex}")

                        with open(f"./logs/_error.txt", 'a', encoding="utf8") as error_file:
                            error_file.write(base_out+"\n")
                            error_file.write(LOG_URL.get() + "\n")
                            error_file.write(f"{fn.__name__}\n")
                            error_file.write(f"{traceback.format_exc()}\n")

        return wrapper
    return decorator

async def human_mouse_move(page, target_x, target_y, steps=25):
    box = await page.evaluate("() => ({w: window.innerWidth, h: window.innerHeight})")
    start_x, start_y = random.randint(0, box["w"]), random.randint(0, box["h"])
    for i in range(steps):
        x = start_x + (target_x - start_x) * i / steps + random.uniform(-3, 3)
        y = start_y + (target_y - start_y) * i / steps + random.uniform(-3, 3)
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.005, 0.02))

@try_and_log_decor("Прокрутка до конца страницы", repeats=3)
async def scroll_to_last(elem_locator: Locator, strore = None):
        """Крутим к последнему элементу, если 5 раз колво не изменилось - далее\n
        strore: kaspi - пропускается"""
        if strore == "kaspi":
            return

        prev_count = 0
        retries = 0
        max_retries = 5
        while retries < max_retries:

            count = await elem_locator.count()
            if count == prev_count:
                retries += 1
            else:
                retries = 0
            prev_count = count

            await elem_locator.nth(count - 1).scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
        # return count

async def nextpage_gen_cards(page: Page, parser_config: ParserConfig): 
    """ Генератор списка локаторов карточек, возвращает locator \n
    card_locator: get_card_locator из парсер конфига \n
    deep: глубина, количество блоков с которых будет собранны данные \n
    """
    @try_and_log_decor("Смена страницы")
    async def go_to_next_page(next_page_button: Locator): 
        await next_page_button.click()

    block = parser_config.get_card_locator(page)
    
    await scroll_to_last(block, parser_config.store)
    # запоминаем размер блока ↓
    item_in_block = await block.count()
    yield block

    pages_completed = 1
    retries = 0
    depth = parser_config.get_max_depth(item_in_block)
    while retries < 3 and pages_completed < depth:
        # ищем кнопку смены страницы - и нажимаем, с ожиданием
        next_page_button = parser_config.get_nextpage_locator(page)
        if await next_page_button.count() > 0:
            await go_to_next_page(next_page_button)
            await wait_page(page, parser_config)
            # пропускаем, если на странице теперь нет результатов (и так бывало)
            if await parser_config.fn_noresults(page):
                break
            # block = parser_config.get_card_locator(page)
            await scroll_to_last(block, parser_config.store)
            yield block
            retries = 0
            pages_completed += 1
            # break
        else:
            await page.wait_for_timeout(200)
            retries +=1

def get_search_urls(base_url: str, book: EBook, isbn_prefix: bool = False, escaping_dash_in_isbn: bool = False) -> list[str]:
    """Генерируем список url для поиска книги, 
    принимает базовый url к которому добавляет данные из объекта книги
    escaping_a_character_in_isbn: экранируем тире в isbn"""

    search_urls = [(str(base_url+book.get_search_text()).replace(" ", "+"), "text")]
    if book.isbns:
        if isbn_prefix:
            base_url += "isbn "
        if book.only_isbn:
             search_urls = []
        for isbn in book.isbns:
            url = base_url.replace(" ", "+")
            url += isbn.replace("-", "\\-") if escaping_dash_in_isbn else isbn
            search_urls.append((url, "isbn"))
        # search_urls.extend( [(base_url.replace(" ", "+")+isbn, "isbn") for isbn in book.isbns] )

    # Затычка сохраняющая ссылки
    for url in search_urls:
        with open(f"./logs/_urls.txt", 'a', encoding="utf8") as file:
            file.write(book.title + " " + url[0] + "\n")
    return search_urls

# TODO  в трае оно, чтобы проверить поведение кода, если обложка не будет получена, а процесс пойдет дальше
@try_and_log_decor("Получение обложки", repeats=3)
async def image_from_response(response: APIResponse):
    content_type = response.headers.get("content-type", "").lower()

    if not content_type.startswith("image/"):
        # Можно логировать или сохранять ошибку
        return None

    # Проверяем статус
    if not response.ok:
        return None
    return await response.body()

@try_and_log_decor("Переход на страницу", repeats=3)
async def goto_url(page: Page, url: str):
    # # один день была ошибка, с flip типо страница не загрузилась, тестируем обход:
    # try:
    #     await page.goto(url)
    # except:
    #     try:
    #         await page.goto(url, wait_until="domcontentloaded")
    #     except:
    #         try:
    #             await page.goto(url, wait_until="commit")
    #         except:
    #             raise

    await page.goto(url)

@try_and_log_decor("Ожидание страницы", repeats=3)
async def wait_page(page: Page, parser_config: ParserConfig):
    await page.wait_for_load_state(parser_config.wait_for_load_stat)
    await page.wait_for_timeout(parser_config.wait_for_load_time)

@try_and_log_decor("Обработка одной карточки", repeats=3)
async def parse_card(page: Page, card: Locator, book: EBook, parser_config: ParserConfig) -> ShopCard:
    # try:
    card_title = await parser_config.get_card_title(card)
    if book.is_TITLE_in_STR(card_title):
        if book.need_check_author:
            card_title = card_title.replace("| Книга б/у", "")
            if parser_config.store == "ozon" and "|" in card_title:
                if book.author and not book.is_AUTHOR_in_STR(card_title):
                    # tqdm.write(f"{await parser_config.get_card_article(card)}   {book.author=}   {card_title=}") #  TODO Для отладки
                    return 
        price = utils.normalizePrice( await parser_config.get_card_price(card) )
        if price is None:
            return
        article = await parser_config.get_card_article(card)
        cover_path = f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}/{book.title.replace(":","")}/{parser_config.store}_{price}_{article}.png"
        cover_bytes = await image_from_response( await parser_config.get_card_cover(card, page) )
        return ShopCard(
            price = price, 
            store = parser_config.store, 
            article = article, 
            cover_path = cover_path, 
            cover_bytes = cover_bytes,
            )
    # except TimeoutError:
    #     raise
    # except Exception as ex:
        # ex.add_note(f"HTML элемента:\n {utils.prettify_html(await card.evaluate('element => element.outerHTML'))}")
        # await card.screenshot(path=f"./logs/{book.title}_{parser_config.store}_{dt.now().strftime("%Y-%m-%d %H-%M")}.png")
    #     raise #ex

@try_and_log_decor("Проваливаемся в карточку и проверяем", repeats=3)
async def check_card(page: Page, card: ShopCard, book: EBook, parser_config: ParserConfig) -> bool:
    # if parser_config.store != "ozon":
    #     return True
    
    # try:
    #     card_page: Page = await page.context.new_page()
    #     await card_page.goto(card.get_url())
    #     await wait_page(card_page, parser_config)

    #     if await card_page.get_by_text("Подтвердите, что вы не бот").count():
    #         tqdm.write(">>> Антибот")
    #         return True
    #     category = await card_page.locator("a[href='/category/knigi-16500/']").count()
    #     if category == 0:
    #         await card_page.wait_for_timeout(1000)
    #         category = await card_page.locator("a[href='/category/knigi-16500/']").count()

    #     if book.author:
    #         author = await card_page.locator('div[data-widget="webShortCharacteristics"]').get_by_text(book.author).count()
    #     else:
    #         author = 1
    #     if category != 0 and author != 0:
    #         return True
    #     tqdm.write(f"Категория: {category}. Автор: {author}. {card.get_url()}")
    #     return False

    # finally:
    #     await card_page.close()
    return True

@try_and_log_decor("Парсим данные: основная функция")
async def run_parser(context: BrowserContext, book: EBook, parser_config: ParserConfig) ->  list[ShopCard]:
    """Парсер, принимает контекст и объект книги, возвращает список объектов с 'карточками'"""
    page = await context.new_page()
    CURRENT_PAGE.set(page)
    all_items = []
    search_urls = get_search_urls(parser_config.base_url, book, parser_config.isbn_prefix, parser_config.isbn_escaping_dash)
    # if parser_config.base_url_alt:
    #     search_urls.extend( get_search_urls(parser_config.base_url_alt, book) )
    ERROR_PREFIX.set(f"{book.title}: {parser_config.store}")
    for url in search_urls:
        LOG_URL.set(url[0])
        await goto_url(page, url[0])

        await wait_page(page, parser_config)

        if await parser_config.fn_extra_goto(page):
            await wait_page(page, parser_config)
            
        await parser_config.fn_extra_wait_cat(page)

        if await parser_config.fn_noresults(page):
            continue

        async for block in parser_config.generator_cards(page, parser_config):
            # Каталог прогружается постранично/поблочно через генератор,
            # возвращающий блок элементов 
            cat = await block.all()
            added = 0 # счетчик добавленных элементов
            # обходим по одному элементу за раз
            for card in cat:
                result = await parse_card(page, card, book, parser_config)
                if result:
                    result.type_search = url[-1]
                    # result.save_cover()
                    all_items.append(result)
                    added += 1
            # если на странице ничего не найдено, на следующюю не идем, 
            # кроме некоторых (озон например, он быстрее грузится и редко, 
            # но бывает наличие нужного элемента где то вконце)
            if added == 0 and parser_config.store not in ["ozon", "wb"]:
                # tqdm.write(f"{parser_config.store}")
                break
            # else:
            #     tqdm.write(f"{parser_config.store} {added=}")
    if parser_config.store.lower() == "wb" and len(all_items) == 0:
        await page.evaluate("window.scrollTo(0, 0)")
        await screen_and_save_page(dir_path = './logs/err/zero', page = page, file_prefix=f"{parser_config.store}_", file_suffix=f"_{book.title}")
    #     input("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    await page.close()
    return all_items

@try_and_log_decor("Создание контекста", repeats=3)
async def run_create_context(context: BrowserContext, parser_config: ParserConfig):
    page = await context.new_page()
    CURRENT_PAGE.set(page)
    ERROR_PREFIX.set(f"{parser_config.store}")
    LOG_URL.set(parser_config.base_url+"Достоевский")
    await goto_url(page, parser_config.base_url+"Достоевский")
    await wait_page(page, parser_config)
    await parser_config.fn_extra_wait_cat(page)
    if sys.platform == "linux":
        await page.wait_for_timeout(1000)
    # if sys.platform == "win32":
    #     if await parser_config.fn_login(page):
    #         await goto_url(page, parser_config.base_url+"Достоевский")
    #         await wait_page(page, parser_config)

    # проверяем и переключаем валюту
    await parser_config.fn_currency(page)
    # указываем адрес
    await parser_config.fn_city(page)

    # if parser_config.store.lower() == "wb":
        # await page.wait_for_url("**/account/**", timeout=0)
        # await asyncio.to_thread(input, "Продолжить? ")
    #     input("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        
    await page.close()
    pass

@try_and_log_decor("Парсим данные ТЕСТ: основная функция")
async def run_parser_test(context: BrowserContext, book: EBook, parser_config: ParserConfig) ->  list[ShopCard]:
    """Парсер, принимает контекст и объект книги, возвращает список объектов с 'карточками'"""
    pass
#         # Кликанье на автора показала себя неэффективно на всех магазинах: 
#         # результатов гораздо меньше, а времени уходит гораздо больше... 
#         # данный блок должен стоять до проверка на noresult
#         # click_author = await parser_config.fn_click_author(page, book.author)
#         # if click_author:
#         #     if click_author == "noresults":
#         #         continue
#         #     await wait_page(page, parser_config)
# 

