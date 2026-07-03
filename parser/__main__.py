import os, sys
if __name__  == '__main__':
    # TODO для отладки
    os.chdir( os.path.abspath( os.path.dirname( os.path.dirname(__file__) ) ) )
    sys.path.append( os.getcwd() )
    # print(os.getcwd())

from parser.common import (
    async_playwright,
    asyncio, dt,
    EBook,
    tqdm, utils
    )

from parser.wb import main as wb
from parser.ozon import main as ozon
from parser.flip import main as flip
from parser.kaspi import main as kaspi

import json

async def __run__(fn, books: EBook|list[EBook], headless = True, test_context = False):
    async with async_playwright() as p:
        state_path = "./parser/state.json"
        if test_context:
            state_path = "./parser/profile/state.json"
        # загружаем состояние контекста
        storage_state = None
        if os.path.exists(state_path):
            storage_state = state_path
        # Контекст задается для все сессии. После некоторые вещи сменить не выйдет. 
        viewport = {"width": 1920, "height": 1080}
        user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
        # user_agent=None
        # if sys.platform == "linux":
        #     user_agent=f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        #     viewport = {"width": 1280, "height": 1024}
        executable_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        executable_path = None

        if not test_context:
            browser = await p.chromium.launch(
                        executable_path=executable_path,
                        # channel="chrome",
                        # channel="chromium",
                        proxy = None,
                        headless = headless,
                        args = [
                        "--start-maximized", 
                        # '--disable-blink-features=AutomationControlled', # дублируется в patchright, включать в playright
                        # "--disable-infobars",
                        "--no-sandbox",
                        # "--disable-dev-shm-usage",
                        "--disable-gpu"
                                ]
                                                )
            
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
                        storage_state = storage_state,
                                                )

            context.my_data = {}
            context.my_data["zero_page"] = await context.new_page()
            # посмотреть юсерагент
            # await context.my_data["zero_page"].goto("https://www.browserscan.net/ru/user-agent")
            # await asyncio.to_thread(input, "Продолжить? ")
            # input("!")

        if test_context:
            context = await p.chromium.launch_persistent_context(
                            executable_path=executable_path,
                            user_data_dir="./parser/profile",
                            user_agent=user_agent,
                            # channel="chrome",
                            headless=headless,
                            viewport=viewport,
                            proxy = None,
                            locale="ru-RU",
                            timezone_id="Asia/Almaty",
                            permissions=["geolocation"],
                            geolocation={"latitude": 52.265415, "longitude": 76.977453},
                            # storage_state = storage_state,
                            args = [
                                "--start-maximized", 
                                "--no-sandbox",
                                # "--disable-dev-shm-usage",
                                "--disable-gpu",
                                # # NOTE: Две опции альтернативной загружки cach/coocki прошлой сессии
                                # '--restore-last-session', 
                                # "--hide-crash-restore-bubble",
                                    ]
                                            )
                                            
            if storage_state:    
                # NOTE: загрузка данных прошлой сессии
                state = json.load(open(storage_state, encoding="utf-8"))
                # cookies = state["cookies"]
                # получаем только ozon state
                cookies = utils.state_filter(state, "ozon.kz")["cookies"]
                await context.add_cookies(cookies)

            context.my_data = {}
            context.my_data["zero_page"] = await context.new_page()
            await context.my_data["zero_page"].goto("https://ozon.kz/product/3909169867/?__rr=1")

        # Создать контекст
        await create_context(context)
        await fn(context, books)

        # сохраняем состояние контекста
        await context.storage_state(path=state_path)

        if not test_context:
            await browser.close()

        if test_context:
            # # NOTE: Закрытие всех страниц, для опции '--restore-last-session'
            # while context.pages:
            #     await context.pages[-1].close()
            await context.close()


async def create_context(context):
     await asyncio.gather(
            wb(context = context, book = None, create_context = True),
            flip(context = context, book = None, create_context = True),
            kaspi(context = context, book = None, create_context = True),
            ozon(context = context, book = None, create_context = True),
             )
     
async def one_book(context, book: EBook):
        # results = await asyncio.gather(
        stores = [
            wb(context = context, book = book),
            wb(context = context, book = book, alter_search = True),
            flip(context = context, book = book),
            kaspi(context = context, book = book),
            ozon(context = context, book = book, alter_search = True),
            ozon(context = context, book = book)
             ]
        # if sys.platform != "linux":
        #     stores.extend([
        #                    ])
        results = await tqdm.gather(*stores,
                                desc=book.title, #tqdm options
                                ncols=80, 
                                leave=False,
                                    )
        for res in results:
            if res:
                book.add_prices(res)
        

async def list_books(context, books: list[EBook]):
        # Паралельный запуск
        pbar = tqdm(books, ncols=80, desc="Парсим книжки")
        for book in pbar:
        # for book in books:
            # print(book.title)
            # pbar.set_description(book.title)

            await one_book(context, book)

def run(books: EBook|list[EBook], headless = True, **kwargs):
    if isinstance(books, list):
         fn = list_books
    if isinstance(books, EBook):
         fn = one_book
    asyncio.run(__run__(
         fn = fn,
         books = books,
         headless = headless,
         **kwargs
           ))

def main():
    pass

if __name__  == '__main__':
    main()

    
            # await context.add_init_script("""
            #         Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            #         Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            #         """)
            # await context.add_init_script("""
            #         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            #         delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
            #         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
            #         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            #         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
            #         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            #         """)
            # await context.add_init_script("""
            #         const style = document.createElement('style');
            #         style.innerHTML = `
            #         * {
            #         animation: none !important;
            #         transition: none !important;
            #         }
            #         `;
            #         document.head
            # .appendChild(style);
            #         """)