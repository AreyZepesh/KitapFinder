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

from shared.paths import PROFILE_DIR

STORE_TASKS = {
    "wb": lambda ctx, book: wb(context=ctx, book=book),
    # "wb_alt": lambda ctx, book: wb(context=ctx, book=book, alter_search=True),ёё
    "flip": lambda ctx, book: flip(context=ctx, book=book),
    "kaspi": lambda ctx, book: kaspi(context=ctx, book=book),
    "ozon": lambda ctx, book: ozon(context=ctx, book=book, alter_search=True),
    "ozon_alt": lambda ctx, book: ozon(context=ctx, book=book),
            }

async def context_extender(context: BrowserContext):
    # tqdm.write(f"{context.browser.version=}")

    # Для Chrome (New) = passed в антиботе
    await context.add_init_script("""if (!window.chrome) {
                            window.chrome = { runtime: {} };
                        }""")

    await context.add_init_script("""Object.defineProperty(navigator, 'plugins', {
                            get: () => {
                                const arr = [1, 2, 3, 4, 5].map(() => ({name: 'Chrome PDF Plugin'}));
                                arr.__proto__ = PluginArray.prototype;
                                return arr;
                            }
                        });""")

    # context.my_data = {}
    # context.my_data["zero_page"] = await context.new_page()
    # # # await context.my_data["zero_page"].goto("https://ozon.kz/product/3909169867")
    # # await context.my_data["zero_page"].goto("https://www.browserscan.net/ru/user-agent")
    # await context.my_data["zero_page"].goto("https://bot.sannysoft.com/")
    # # await asyncio.to_thread(input, "Продолжить? ")
    # input("!")

@asynccontextmanager
async def browser_context(headless: bool = True, persistent_context: bool = True, save_state: bool = True):
    """Открывает браузер/контекст, гарантированно закрывает при выходе.
    save_state=False — не сохранять storage_state (полезно при пересоздании после сбоя,
    чтобы не записать 'плохое' состояние поверх рабочего,
    для пересоздания браузера для одной страницы (антибот))."""
    async with async_playwright() as p:
        state_path = PROFILE_DIR/"state_no_persistent.json"
        if persistent_context:
            state_path = PROFILE_DIR/"state_persistent.json"
        # загружаем состояние контекста
        storage_state = None
        if state_path.exists():
            storage_state = state_path
        # Контекст задается для все сессии. После некоторые вещи сменить не выйдет.
        viewport = {"width": 1920, "height": 1080}
        # user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
        user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
        # user_agent=None
        # if sys.platform == "linux":
        #     user_agent=f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        #     viewport = {"width": 1280, "height": 1024}
        executable_path = None
        # executable_path = r"C:\Users\AreyZepesh\AppData\Local\ms-playwright\chromium-1223\chrome-win64\chrome.exe"
        # # executable_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        # if not os.path.exists(executable_path):
        #     executable_path = None
        channel = "chromium"
        args = [
            "--start-maximized",
            "--no-sandbox",
            # "--disable-dev-shm-usage",
            "--disable-gpu",
            "--use-gl=swiftshader" # NOTE: для сервера и может понадобится подложить правдоподобный UNMASKED_RENDERER_WEBGL через init-script
            # # NOTE: Две опции альтернативной загрузки cach/coocki прошлой сессии
            # '--restore-last-session',
            # "--hide-crash-restore-bubble",
                ]
        if persistent_context:
            context = await p.chromium.launch_persistent_context(
                            executable_path=executable_path,
                            user_data_dir=str(PROFILE_DIR),
                            user_agent=user_agent,
                            channel=channel,
                            headless=headless,
                            viewport=viewport,
                            proxy = None,
                            locale="ru-RU",
                            timezone_id="Asia/Almaty",
                            permissions=["geolocation"],
                            geolocation={"latitude": 52.265415, "longitude": 76.977453},
                            ignore_https_errors = True, # NOTE: test ignore tsl
                            # storage_state = storage_state,
                            args = args,)
            if storage_state:
                # NOTE: загрузка данных прошлой сессии
                state = json.load(open(storage_state, encoding="utf-8"))
                # cookies = state["cookies"]
                # получаем только ozon state
                cookies = state_filter(state, OZON_COOKIE_DOMAIN)["cookies"]
                await context.add_cookies(cookies)
        else:
            browser = await p.chromium.launch(
                        executable_path=executable_path,
                        channel=channel,
                        proxy = None,
                        headless = headless,
                        args = args,)
            context = await browser.new_context(
                        viewport=viewport,
                        # no_viewport=True,
                        user_agent=user_agent,
                        permissions=["geolocation"],  # разрешаем
                        # # geolocation={"latitude": 43.238949, "longitude": 76.889709},  # Алматы :)
                        geolocation={"latitude": 52.265415, "longitude": 76.977453},  # Павлодар, Ломова 154
                        locale="ru-RU",
                        timezone_id="Asia/Almaty",
                        # java_script_enabled=True,
                        device_scale_factor=1,
                        is_mobile=False,
                        storage_state = storage_state,)

        await context_extender(context)

        try:
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

async def run_books_with_recovery(books: EBook|list[EBook], headless: bool = True, persistent_context: bool = True, max_restarts: int = 3):
    failed_queue: list[tuple[EBook, list[str]]] = []

    # Основной проход — НИКОГДА не прерывается из-за антибота на одной книге/магазине
    async with browser_context(headless, persistent_context, save_state=True) as context:
        pbar = tqdm(books, ncols=80, desc="Парсим книжки")
        for book in pbar:
            pbar.set_description(book.title)
            failed = await one_book(context, book)
            if failed:
                failed_queue.append((book, failed))

    # Повторный проход — отдельный браузер, только для того, что реально упало
    retry_pass = 0
    while failed_queue and retry_pass < max_restarts:
        retry_pass += 1
        tqdm.write(f"\n\nПовтор после антибота: {len(failed_queue)} книг/магазинов (попытка {retry_pass})")
        still_failed = []
        async with browser_context(headless, persistent_context, save_state=True) as context:
            pbar = tqdm(failed_queue, ncols=80, desc="Повтор")
            for book, labels in pbar:
                pbar.set_description(book.title)
                new_failed = await one_book(context, book, labels=labels)
                if new_failed:
                    still_failed.append((book, new_failed))
        failed_queue = still_failed

    if failed_queue:
        tqdm.write(f"Не удалось получить данные для {len(failed_queue)} книг/магазинов даже после повтора")


async def create_webcontext(context):
     await asyncio.gather(
            wb(context = context, book = None, create_context = True),
            flip(context = context, book = None, create_context = True),
            kaspi(context = context, book = None, create_context = True),
            ozon(context = context, book = None, create_context = True),
            return_exceptions=True,
            )


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

def run(books: EBook|list[EBook], headless: bool = True, persistent_context: bool = True, **kwargs):
    books_list = books if isinstance(books, list) else [books]
    asyncio.run(run_books_with_recovery(books_list, headless=headless, persistent_context=persistent_context, **kwargs))

if __name__  == '__main__':
    pass
