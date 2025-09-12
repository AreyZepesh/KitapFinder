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
from parser.kaspi import kaspi

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
                    # viewport={"width": 900, "height": 1600},
                    no_viewport=True,
                    # user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
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
                ozon(context = context, book = book),
                flip(context = context, book = book),
                kaspi(context = context, book = book),
                wb(context = context, book = book),
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
    if os.path.exists("./logs/_urls.txt"):
        os.remove("./logs/_urls.txt")
    time_start = dt.now().strftime("%Y-%m-%d %H-%M")

    books = []
    for book in all_book:
        books.append(EBook(**book))
    books.extend( [
        EBook(**{'title': 'Элантрис', 'author': 'Сандерсон', 'isbns': ['978-5-389-20277-1'], 'only_isbn': False},),
        EBook(**{'title': 'Космер. Тайная история', 'author': 'Сандерсон', 'isbns': ['978-5-389-23731-5'], 'only_isbn': False},),
        EBook(**{'title': 'Убийца войн', 'author': 'Сандерсон', 'isbns': ['978-5-389-20180-4'], 'only_isbn': False},),
        EBook(**{'title': 'Локон с Изумрудного моря', 'author': 'Сандерсон', 'isbns': ['978-5-389-22923-5'], 'only_isbn': False},),
        EBook(**{'title': 'Юми и укротитель кошмаров', 'author': 'Сандерсон', 'isbns': ['978-5-389-24688-1'], 'only_isbn': False},),
        EBook(**{'title': 'Озаренный Солнцем', 'author': 'Сандерсон', 'isbns': ['978-5-389-25650-7'], 'only_isbn': False},),
        EBook(**{'title': 'Вы чародей', 'author': 'Сандерсон', 'isbns': ['978-5-389-22922-8'], 'only_isbn': False},),
        EBook(**{'title': 'Легион', 'author': 'Сандерсон', 'isbns': ['978-5-389-16903-6'], 'only_isbn': False},),
        EBook(**{'title': 'Тираны и мстители', 'author': 'Сандерсон', 'isbns': ['978-5-389-23257-0'], 'only_isbn': False},),
        EBook(**{'title': 'Устремленная в небо', 'author': 'Сандерсон', 'isbns': ['978-5-389-16425-3'], 'only_isbn': False},),
        EBook(**{'title': 'Видящая звезды', 'author': 'Сандерсон', 'isbns': ['978-5-389-18074-1'], 'only_isbn': False},),
        EBook(**{'title': 'Цитоник', 'author': 'Сандерсон', 'isbns': ['978-5-389-23598-4'], 'only_isbn': False},),
        EBook(**{'title': 'Звездная Эскадрилья', 'author': 'Сандерсон', 'isbns': ['978-5-389-26184-6'], 'only_isbn': False},),

        # EBook(**{'title': 'Сады Луны', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Врата Мёртвого Дома', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Врата смерти', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Память льда', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Дом Цепей', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Полночный прилив', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Полуночный Прилив', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Охотники за костями', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Буря Жнеца', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Дань псам', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Пыль грёз', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Пыль Снов', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Увечный бог', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),

        EBook("Новый Дозор", "Лукьяненко", ['978-5-271-41900-3', '978-5-17-118480-3']),
        EBook("Шестой Дозор", "Лукьяненко", ['978-5-17-088817-7', '978-5-17-118536-7']),
        ] )

    # books = [
    #     EBook("Преступление и наказание", "Достоевский"), 
    #     EBook("Ключ из желтого металла", "Фрай"),
    #     EBook(**{'title': 'Вы чародей', 'author': 'Сандерсон', 'isbns': ['978-5-389-22922-8'], 'only_isbn': False},),
    #     ]

    headless = False
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