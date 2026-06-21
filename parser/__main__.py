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
    tqdm,
    )

from parser.wb import main as wb
from parser.ozon import main as ozon
from parser.flip import main as flip
from parser.kaspi import main as kaspi

async def __run__(fn, books: EBook|list[EBook], headless = True):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
                    channel="chrome",
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
        
        # загружаем состояние контекста
        storage_state = None
        if os.path.exists("./parser/state.json"):
            storage_state = "./parser/state.json"

        # Контекст задается для все сессии. После некоторые вещи сменить не выйдет. 
        viewport = {"width": 1920, "height": 1080}
        # user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
        user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
        # if sys.platform == "linux":
        #     user_agent=f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        #     viewport = {"width": 1280, "height": 1024}

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
        #         document.head.appendChild(style);
        #         """)
        context.my_data = {}
        context.my_data["zero_page"] = await context.new_page()
        
        # посмотреть юсерагент
        # await context.my_data["zero_page"].goto("https://www.browserscan.net/ru/user-agent")
        # input("!")

        # Создать контекст
        await asyncio.gather(
            wb(context = context, book = None, create_context = True),
            flip(context = context, book = None, create_context = True),
            kaspi(context = context, book = None, create_context = True),
            ozon(context = context, book = None, create_context = True),
             )


        await fn(context, books)

        # сохраняем состояние контекста
        await context.storage_state(path="./parser/state.json")

        await browser.close()


async def one_book(context, book: EBook):
        # results = await asyncio.gather(
        stores = [
            wb(context = context, book = book),
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

def run(books: EBook|list[EBook], headless = True):
    if isinstance(books, list):
         fn = list_books
    if isinstance(books, EBook):
         fn = one_book
    asyncio.run(__run__(
         fn = fn,
         books = books,
         headless = headless
           ))

def main():
    pass

if __name__  == '__main__':
    main()