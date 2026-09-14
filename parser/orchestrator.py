import os
import asyncio
import json
# import dt
from tqdm.asyncio import tqdm
from patchright.async_api import async_playwright, BrowserContext

from parser.domain import EBook
from parser.utils import state_filter
from parser.stores.wb import main as wb
from parser.stores.ozon import main as ozon, COOKIE_DOMAIN as OZON_COOKIE_DOMAIN
from parser.stores.flip import main as flip
from parser.stores.kaspi import main as kaspi
from shared.paths import PROFILE_DIR

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

async def __run__(fn, books: EBook|list[EBook], headless = True, persistent_context = True):
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

        if not persistent_context:
            browser = await p.chromium.launch(
                        executable_path=executable_path,
                        channel=channel,
                        proxy = None,
                        headless = headless,
                        args = args,
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
            
            await context_extender(context)
            

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
                            args = args,
                                )
            
            if storage_state:    
                # NOTE: загрузка данных прошлой сессии
                state = json.load(open(storage_state, encoding="utf-8"))
                # cookies = state["cookies"]
                # получаем только ozon state
                cookies = state_filter(state, OZON_COOKIE_DOMAIN)["cookies"]
                await context.add_cookies(cookies)

            await context_extender(context)

        # Создать контекст
        await create_context(context)
        await fn(context, books)

        # сохраняем состояние контекста
        await context.storage_state(path=state_path)

        if not persistent_context:
            await browser.close()

        if persistent_context:
            # # NOTE: Закрытие всех страниц, для опции '--restore-last-session'
            # while context.pages:
            #     await context.pages[-1].close()
            await context.close()


async def create_context(context):
    # await wb(context = context, book = None, create_context = True)
    # await flip(context = context, book = None, create_context = True)
    # await kaspi(context = context, book = None, create_context = True)
    # await ozon(context = context, book = None, create_context = True)
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
    
if __name__  == '__main__':
    pass

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