import os
import asyncio
import json
# import dt
from tqdm.asyncio import tqdm
from patchright.async_api import async_playwright, BrowserContext
from contextlib import asynccontextmanager

from parser.domain import EBook
from parser.utils import state_filter
from parser.exceptions import ParserControlException, AntibotDetectedError
from parser.stores.wb import main as wb
from parser.stores.ozon import main as ozon, COOKIE_DOMAIN as OZON_COOKIE_DOMAIN
from parser.stores.flip import main as flip
from parser.stores.kaspi import main as kaspi
from parser.engine import screen_and_save_page

from shared.paths import PROFILE_DIR, TMP_DIR, LOGS_DIR

STORE_TASKS = {
    "wb": lambda ctx, book: wb(context=ctx, book=book),
    # "wb_alt": lambda ctx, book: wb(context=ctx, book=book, alter_search=True),
    "flip": lambda ctx, book: flip(context=ctx, book=book),
    "kaspi": lambda ctx, book: kaspi(context=ctx, book=book),
    "ozon": lambda ctx, book: ozon(context=ctx, book=book, alter_search=True),
    "ozon_alt": lambda ctx, book: ozon(context=ctx, book=book),
            }

async def create_zero_page(context: BrowserContext):
    context.my_data = {}
    context.my_data["zero_page"] = await context.new_page()
    zero_page = TMP_DIR/"zero_page.html"
    await context.my_data["zero_page"].goto(zero_page if zero_page.exists() else "https://abrahamjuliot.github.io/creepjs/")
    await asyncio.to_thread(input, "Продолжить? ")
    await screen_and_save_page(dir_path = LOGS_DIR/'zero_page', page = context.my_data["zero_page"], file_prefix=f"zero_")

def get_browser_kwargs(headless: bool = True, persistent_context: bool = True):
    viewport =  None
    # viewport = {"width": 1920, "height": 1080}

    user_agent=None
    # user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    # user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"

    executable_path = None
    # executable_path = r"C:\Users\AreyZepesh\AppData\Local\ms-playwright\chromium-1223\chrome-win64\chrome.exe"
    # executable_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    # if not os.path.exists(executable_path):
    #     executable_path = None

    channel = "chromium"
    # channel = "chrome"

    args = [
        "--start-maximized",
        "--no-sandbox",
        "--disable-blink-features=AutomationControlled",
        # "--disable-dev-shm-usage",
        "--disable-gpu",

        "--use-gl=swiftshader" 
        # NOTE: для сервера и может понадобится подложить 
        # правдоподобный UNMASKED_RENDERER_WEBGL через init-script

        # # NOTE: Две опции альтернативной загрузки cach/coocki прошлой сессии
        # '--restore-last-session',
        # "--hide-crash-restore-bubble",
            ]
    
    browser_kwargs = dict(
        executable_path=executable_path,
        channel=channel,
        proxy = None,
        headless = headless,
        args = args
                        )
    
    context_kwargs = dict(
        user_agent=user_agent,
        viewport=viewport,
        no_viewport=None if viewport else True,
        locale="ru-RU",
        timezone_id="Asia/Almaty",
        permissions=["geolocation"],  # разрешаем
        # # geolocation={"latitude": 43.238949, "longitude": 76.889709},  # Алматы :)
        geolocation={"latitude": 52.265415, "longitude": 76.977453},  # Павлодар, Ломова 154
        ignore_https_errors = True, 
                        )
    
    if persistent_context:
        browser_kwargs["user_data_dir"]=str(PROFILE_DIR)
    
    return browser_kwargs, context_kwargs
    

@asynccontextmanager
async def browser_context(headless: bool = True, persistent_context: bool = True, save_state: bool = True, need_zero_page: bool = False):
    """Открывает браузер/контекст, гарантированно закрывает при выходе.
    save_state=False — не сохранять storage_state (полезно при пересоздании после сбоя,
    чтобы не записать 'плохое' состояние поверх рабочего,
    для пересоздания браузера для одной страницы (антибот))."""
    async with async_playwright() as p:
        state_path = PROFILE_DIR/"state_no_persistent.json"
        if persistent_context:
            state_path = PROFILE_DIR/"state_persistent.json"

        storage_state = None
        if state_path.exists():
            storage_state = state_path

        browser_kwargs, context_kwargs= get_browser_kwargs(headless=headless, persistent_context=persistent_context)
        
        if persistent_context:
            context = await p.chromium.launch_persistent_context( 
                **{**browser_kwargs, **context_kwargs} )
            if storage_state:
                # NOTE: загрузка данных прошлой сессии
                state = json.load(open(storage_state, encoding="utf-8"))
                # cookies = state["cookies"]
                # получаем только ozon state
                cookies = state_filter(state, OZON_COOKIE_DOMAIN)["cookies"]
                await context.add_cookies(cookies)
        else:
            browser = await p.chromium.launch(
                        **browser_kwargs
                        )
            context = await browser.new_context(storage_state=storage_state,
                                                **context_kwargs)

        await context.add_init_script("""if (!window.chrome) {
                            window.chrome = { runtime: {} };
                        }""")
        
        context.window_box = {}
        
        try:
            if need_zero_page:
                await create_zero_page(context)
            # Создать webконтекст
            await create_webcontext(context)
            yield context
        finally:
            if save_state:
                await context.storage_state(path=state_path)

            if persistent_context:
                await context.close()
                # # NOTE: Закрытие всех страниц, для опции '--restore-last-session'
                # while context.pages:
                #     await context.pages[-1].close()
            else:
                await browser.close()

async def run_books_with_recovery(books: EBook|list[EBook], headless: bool = True, persistent_context: bool = True, max_restarts: int = 3, need_zero_page: bool = False):
    failed_queue: list[tuple[EBook, list[str]]] = []

    # Основной проход — НИКОГДА не прерывается из-за антибота на одной книге/магазине
    async with browser_context(headless, persistent_context, need_zero_page = need_zero_page) as context:
        pbar = tqdm(books, ncols=80, desc="Парсим книжки")
        for book in pbar:
            pbar.set_description(f"{book.title[:40]}")
            failed = await one_book(context, book)
            if failed:
                failed_queue.append((book, failed))

    # Повторный проход — отдельный браузер, только для того, что реально упало
    retry_pass = 0
    while failed_queue and retry_pass < max_restarts:
        retry_pass += 1
        tqdm.write(f"\n\nПовтор после антибота: {len(failed_queue)} книг/магазинов (попытка {retry_pass})")
        still_failed = []
        async with browser_context(headless, persistent_context) as context:
            pbar = tqdm(failed_queue, ncols=80, desc="Повтор")
            for book, labels in pbar:
                pbar.set_description(f"{book.title[:40]}")
                new_failed = await one_book(context, book, labels=labels)
                if new_failed:
                    still_failed.append((book, new_failed))
        failed_queue = still_failed

    if failed_queue:
        tqdm.write(f"Не удалось получить данные для {len(failed_queue)} книг/магазинов даже после повтора")


async def create_webcontext(context):
     results = await asyncio.gather(
            wb(context = context, book = None, create_context = True),
            flip(context = context, book = None, create_context = True),
            kaspi(context = context, book = None, create_context = True),
            ozon(context = context, book = None, create_context = True),
            return_exceptions=True,
            )
     
     for res in results:
        if isinstance(res, Exception):
            tqdm.write(f"Прогрев магазина не удался: {res!r}")


async def one_book(context, book: EBook, labels: list[str] | None = None) -> list[str]:
    """Обрабатывает книгу по указанным (или всем) магазинам.
    Возвращает список labels, которые упали с антиботом — для повторной попытки."""
    labels = labels or list(STORE_TASKS.keys())
    tasks = [STORE_TASKS[label](context, book) for label in labels]

    # return_exceptions=True — исключение НЕ вылетает из gather наружу,
    # поэтому browser_context не разрушается из-за одного упавшего магазина,
    # и проблема с "брошенным соседом" (TargetClosedError) не возникает вообще
    # results = await tqdm.gather(*tasks, desc=book.title, ncols=80, leave=False, return_exceptions=True)
    results = await asyncio.gather(*tasks, return_exceptions=True)

    failed = []
    # NOTE: Осторожно, цикл будет работать, только если не нарушен порядок таск и результатов
    for label, res in zip(labels, results):
        if isinstance(res, AntibotDetectedError):
            failed.append(label)
        elif isinstance(res, Exception):
            continue  # обычная ошибка — уже залогирована внутри run_parser декоратором
        elif res:
            book.add_prices(res)
    return failed

def run(books: EBook|list[EBook], headless: bool = True, persistent_context: bool = True, need_zero_page: bool = False):
    books_list = books if isinstance(books, list) else [books]
    asyncio.run(run_books_with_recovery(books_list, headless=headless, persistent_context=persistent_context, need_zero_page = need_zero_page))

if __name__  == '__main__':
    pass
