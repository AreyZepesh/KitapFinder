import os, sys
os.chdir( os.path.abspath( os.path.dirname( os.path.dirname(__file__) ) ) )
sys.path.append( os.getcwd() )

# print(os.getcwd())

from parser.common import (
    async_playwright, expect,
    asyncio, 
    utils,
    EBook, ShopCard,
    scroll_to_last,
    )

from parser.wb import wb

async def async_work(books: list[EBook]):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
                    headless=False,
                    args=[
                    "--start-maximized", 
                    '--disable-blink-features=AutomationControlled',
                    # "--disable-infobars",
                    "--no-sandbox",
                    # "--disable-dev-shm-usage",
                    "--disable-gpu"
                            ]
                                            )
        
        # Контекст задается для все сессии. После некоторые вещи сменить не выйдет. 
        # Например разрешение 1600*900 отлично подходит для wb, а для других? TODO
        context = await browser.new_context(
                    viewport={"width": 1600, "height": 900},
                    no_viewport=True,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    locale="ru-RU",
                    timezone_id="Asia/Almaty",
                    # java_script_enabled=True,
                    # device_scale_factor=1,
                    # is_mobile=False,
                                            )
        zero_page = await context.new_page()
        # await zero_page.goto("")
        # Паралельный запуск
        for book in books:
            print(book.title)

            results = await asyncio.gather(
                wb(context = context, book = book),
                # ozon(context),
                                        )
            # wblist = results[0]
            # Последовательный запуск
            # wblist = await wb(context=context, hardCover=True)


            # x = input("send anything") 

            for res in results:
                book.add_prices(res)

        # wbpage = await context.new_page()
        
        await browser.close()

def main():
    from test_books import all_book

    books = []
    for book in all_book:
        books.append(EBook(**book))
    books = [EBook("Преступление и наказание", "Достоевский"), EBook("Ключ из желтого металла", "Фрай")]
    asyncio.run(async_work(books=books))
    x = input("send anything") 
    for b in books:
        print(b.title, len(b.prices))
        # for p in b.prices:
        #     print(p.to_dict())
        #     print(p.get_url())
        # print()
        # print(b)

if __name__  == '__main__':
    main()