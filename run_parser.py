from models import EBook, ShopCard
from test_books import all_book
from utils import save_objects, save_image_from_bytes

from shutil import rmtree
import os
from datetime import datetime as dt
from parser import run

def main():
    if os.path.exists("./logs/_urls.txt"):
        os.remove("./logs/_urls.txt")
    if os.path.exists(f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}"):
        rmtree(f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}")
    if os.path.exists(f"./logs/_nores"):
        rmtree(f"./logs/_nores")
    time_start = dt.now().strftime("%Y-%m-%d %H-%M")

    books = []
    for book in all_book:
        books.append(EBook(**book))
    books.extend( [
        EBook(**{'title': 'Элантрис', 'author': 'Сандерсон', 'isbns': ['978-5-389-20277-1'], 'only_isbn': False},),
        EBook(**{'title': 'Космер. Тайная история', 'author': 'Сандерсон', 'isbns': ['978-5-389-23731-5'], 'only_isbn': False},),
        EBook(**{'title': 'Убийца войн', 'author': 'Сандерсон', 'isbns': ['978-5-389-20180-4'], 'only_isbn': False},),
        EBook(**{'title': 'Легион', 'author': 'Сандерсон', 'isbns': ['978-5-389-16903-6'], 'only_isbn': False},),
        EBook(**{'title': 'Устремленная в небо', 'author': 'Сандерсон', 'isbns': ['978-5-389-16425-3'], 'only_isbn': False},),
        EBook(**{'title': 'Видящая звезды', 'author': 'Сандерсон', 'isbns': ['978-5-389-18074-1'], 'only_isbn': False},),
        EBook(**{'title': 'Цитоник', 'author': 'Сандерсон', 'isbns': ['978-5-389-23598-4'], 'only_isbn': False},),
        EBook(**{'title': 'Звездная Эскадрилья', 'author': 'Сандерсон', 'isbns': ['978-5-389-26184-6'], 'only_isbn': False},),

        EBook(**{'title': 'Сады Луны', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Врата Мёртвого Дома', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Врата смерти', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Память льда', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Дом Цепей', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Полночный прилив', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Полуночный Прилив', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Охотники за костями', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Буря Жнеца', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Дань псам', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Пыль грёз', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Пыль Снов', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Увечный бог', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),

        EBook("Новый Дозор", "Лукьяненко", ['978-5-271-41900-3', '978-5-17-118480-3']),
        EBook("Шестой Дозор", "Лукьяненко", ['978-5-17-088817-7', '978-5-17-118536-7']),

        EBook(**{'title': 'Волки Кальи+', 'author': 'Кинг', 'isbns': ['978-5-17-133881-7'], 'only_isbn': False}),
        EBook(**{'title': 'Песнь Сюзанны+', 'author': 'Кинг', 'isbns': ['978-5-17-133029-3'], 'only_isbn': False}),
        ] )

    # books = [
    #     # EBook("Преступление и наказание", "Достоевский"), 
    #     # EBook("Ключ из желтого металла", "Фрай"),
    # #     # EBook(**{'title': 'Волки Кальи+', 'author': 'Кинг', 'isbns': ['978-5-17-133881-7'], 'only_isbn': False}),
    # #     # EBook(**{'title': 'Песнь Сюзанны+', 'author': 'Кинг', 'isbns': ['978-5-17-133029-3'], 'only_isbn': False}),
    
    #     ]

    # books = EBook("Преступление и наказание", "Достоевский")

    # TODO asyncio.run(async_work(books=books, headless = headless))
    run(books=books, headless = True)
    
    # x = input("send anything") 
    for b in books:
        b.sort_by_price()
        text = f"{b.title}: {len(b.prices)}\n"
        with open(f"./logs/resutls_{time_start}.txt", 'a', encoding="utf8") as file:
            # print(text)
            file.write(text)
            for p in b.prices:
                # print(p.to_dict())
                # print(p.get_url())
                file.write(f"{p.price}: {p.get_url()} ({p.type_search})\n")
            file.write(f"\n")

        # for p in b.prices:
        #     #TODO photo
        #     from pathlib import Path
        #     Path(p.screen_file).parent.mkdir(parents=True, exist_ok=True)
        #     save_image_from_bytes(p.cover_bytes, p.screen_file) 


    print(time_start)
    print(dt.now().strftime("%Y-%m-%d %H-%M"))

    save_objects("./tmp/data.pkl", books)

    for b in books:
        b.optimize_stores_by_cover()
        b.save_covers()
    print(dt.now().strftime("%Y-%m-%d %H-%M"))

if __name__  == '__main__':
    main()