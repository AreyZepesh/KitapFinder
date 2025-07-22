import os, sys
os.chdir( os.path.abspath( os.path.dirname( os.path.dirname(__file__) ) ) )
sys.path.append( os.getcwd() )

# print(os.getcwd())

from parser.common import (
    async_playwright, expect,
    asyncio, datetime as dt,
    utils,
    EBook, ShopCard,
    scroll_to_last,
    )

from parser.wb import wb
from parser.ozon import ozon
from parser.flip import flip

async def async_work(books: list[EBook], headless = False):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
                    headless = headless,
                    args = [
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
                    # viewport={"width": 1920, "height": 1080},
                    no_viewport=True,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    locale="ru-RU",
                    timezone_id="Asia/Almaty",
                    # java_script_enabled=True,
                    # device_scale_factor=1,
                    # is_mobile=False,
                                            )
        context.my_data = {}
        zero_page = await context.new_page()

        # Паралельный запуск
        for book in books:
            print(book.title)

            results = await asyncio.gather(
                wb(context = context, book = book),
                ozon(context = context, book = book),
                flip(context = context, book = book),
                                        )
            # wblist = results[0]
            # Последовательный запуск
            # wblist = await wb(context=context, hardCover=True)


            # x = input("send anything") 

            for res in results:
                book.add_prices(res)

        page = await context.new_page()

        await browser.close()

def main():
    from test_books import all_book

    time_start = dt.now().strftime("%Y-%m-%d %H-%M")

    books = []
    for book in all_book:
        books.append(EBook(**book))
    # books = [
    #     EBook("Преступление и наказание", "Достоевский"), 
    #     EBook("Ключ из желтого металла", "Фрай"),
    #     ]
    # books = [
    #     EBook(**{'title': 'Мечи дня и ночи', 'author': 'Дэвид Геммел', 'isbns': ['5-9578-3095-X']}),
    #     EBook(**{'title': 'Виртуальный свет. Идору. Все вечеринки завтрашнего дня', 'author': 'Гибсон', 'isbns': ['978-5-389-22043-0']}),
    #     EBook(**{'title': 'Мечи против колдовства', 'author': 'Сага о Фафхрде и Сером Мышелове Фриц Лейбер', 'isbns': ['978-5-389-21407-1']}),
    #     EBook(**{'title': 'Машина различий', 'author': 'Гибсон Стерлинг', 'isbns': ['978-5-389-08318-9', '978-5-389-23683-7']}),
    #     # EBook(**),
    #     ]
    headless = True
    asyncio.run(async_work(books=books, headless = headless))
    # x = input("send anything") 
    for b in books:
        b.sort_by_price()
        text = f"{b.title}: {len(b.prices)}\n"
        with open(f"./logs/resutls_{dt.now().strftime("%Y-%m-%d %H-%M")}.txt", 'a', encoding="utf8") as file:
            # print(text)
            file.write(text)
            for p in b.prices:
                # print(p.to_dict())
                # print(p.get_url())
                file.write(f"{p.price}: {p.get_url()} ({p.type_search})\n")
            file.write(f"\n")


    print(time_start)
    print(dt.now().strftime("%Y-%m-%d %H-%M"))

if __name__  == '__main__':
    main()