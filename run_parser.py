from models import EBook, ShopCard
from z_test_books import all_book
from utils import save_objects, save_image_from_bytes
from services.html_generator import render_html_page

from shutil import rmtree
import os
from datetime import datetime as dt
from parser import run

def main():
    if os.path.exists("./logs/_urls.txt"):
        os.remove("./logs/_urls.txt")
    if os.path.exists("./logs/_error.txt"):
        os.remove("./logs/_error.txt")
    if os.path.exists(f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}"):
        rmtree(f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}")
    if os.path.exists(f"./tmp/SCREEN-ALT-{dt.now().strftime("%Y-%m-%d")}"):
        rmtree(f"./tmp/SCREEN-ALT-{dt.now().strftime("%Y-%m-%d")}")
    if os.path.exists(f"./logs/_nores"):
        rmtree(f"./logs/_nores")
    time_start = dt.now().strftime("%Y-%m-%d %H-%M")

    books = []
    for book in all_book:
        books.append(EBook(**book))
    books.extend( [
        EBook(**{'title': 'Портал Теней', 'author': 'Кук', 'isbns': ['978-5-389-17122-0'], 'only_isbn': False},),

        EBook(**{'title': 'Осколок Зари', 'author': 'Сандерсон', 'isbns': ['978-5-389-26180-8'], 'only_isbn': False},),
        EBook(**{'title': 'Космер. Тайная история', 'author': 'Сандерсон', 'isbns': ['978-5-389-23731-5'], 'only_isbn': False},),
        EBook(**{'title': 'Убийца войн', 'author': 'Сандерсон', 'isbns': ['978-5-389-20180-4'], 'only_isbn': False},),
        EBook(**{'title': 'Легион', 'author': 'Сандерсон', 'isbns': ['978-5-389-16903-6'], 'only_isbn': False},),
        EBook(**{'title': 'Устремленная в небо', 'author': 'Сандерсон', 'isbns': ['978-5-389-16425-3'], 'only_isbn': False},),
        EBook(**{'title': 'Видящая звезды', 'author': 'Сандерсон', 'isbns': ['978-5-389-18074-1'], 'only_isbn': False},),
        EBook(**{'title': 'Цитоник', 'author': 'Сандерсон', 'isbns': ['978-5-389-23598-4'], 'only_isbn': False},),
        EBook(**{'title': 'Звездная Эскадрилья', 'author': 'Сандерсон', 'isbns': ['978-5-389-26184-6'], 'only_isbn': False},),
        EBook(**{'title': 'Талант под прикрытием', 'author': 'Сандерсон', 'isbns': ['978-5-389-27681-9'], 'only_isbn': False},),
        EBook(**{'title': 'Киборги Нотариуса', 'author': 'Сандерсон', 'isbns': ['978-5-389-27682-6'], 'only_isbn': False},),
        EBook(**{'title': 'Рыцари Кристаллии', 'author': 'Сандерсон', 'isbns': ['978-5-389-27683-3'], 'only_isbn': False},),

        EBook(**{'title': 'Сады Луны', 'author': 'Эриксон', 'isbns': ['978-5-389-20717-2'], 'only_isbn': False},),
        EBook(**{'title': 'Врата Мёртвого Дома', 'author': 'Эриксон', 'isbns': ['978-5-389-21003-5'], 'only_isbn': False},),
        # EBook(**{'title': 'Врата смерти', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Память льда', 'author': 'Эриксон', 'isbns': ['978-5-389-21278-7'], 'only_isbn': False},),
        EBook(**{'title': 'Дом Цепей', 'author': 'Эриксон', 'isbns': ['978-5-389-23239-6'], 'only_isbn': False},),
        # EBook(**{'title': 'Полночный прилив', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Полуночный Прилив', 'author': 'Эриксон', 'isbns': ['978-5-389-23761-2'], 'only_isbn': False},),
        # EBook(**{'title': 'Охотники за костями', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Буря Жнеца', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Дань псам', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Пыль грёз', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Пыль Снов', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        # EBook(**{'title': 'Увечный бог', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'След крови', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},),

        EBook(**{'title': 'Пробуждение Левиафана', 'author': 'Кори', 'isbns': ['978-5-389-26449-6'], 'only_isbn': False},),
        EBook(**{'title': 'Война Калибана', 'author': 'Кори', 'isbns': ['978-5-389-26911-8'], 'only_isbn': False},),
        EBook(**{'title': 'Врата Абаддона', 'author': 'Кори', 'isbns': ['978-5-389-26910-1'], 'only_isbn': False},),
        EBook(**{'title': 'Пожар Сиболы', 'author': 'Кори', 'isbns': ['978-5-389-27730-4'], 'only_isbn': False},),
        EBook(**{'title': 'Игры Немезиды', 'author': 'Кори', 'isbns': ['978-5-389-27731-1'], 'only_isbn': False},),
        EBook(**{'title': 'Пепел Вавилона', 'author': 'Кори', 'isbns': ['978-5-389-27732-8'], 'only_isbn': False},),

        EBook(**{'title': 'Короли Жути', 'author': 'Имс', 'isbns': ['978-5-389-13190-3'], 'only_isbn': False},),
        EBook(**{'title': 'Кровавая Роза', 'author': 'Имс', 'isbns': ['978-5-389-16829-9'], 'only_isbn': False},),

        EBook(**{'title': 'Титус Гроан', 'author': 'Пик', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Горменгаст', 'author': 'Пик', 'isbns': [], 'only_isbn': False},),
        EBook(**{'title': 'Титус один', 'author': 'Пик', 'isbns': [], 'only_isbn': False},),

        EBook(**{'title': 'Легионы Калара', 'author': 'Батчер', 'isbns': ['978-5-389-24326-2'], 'only_isbn': False},),
        EBook(**{'title': 'Фурии командира', 'author': 'Батчер', 'isbns': ['978-5-389-25018-5'], 'only_isbn': False},),
        EBook(**{'title': 'Фурии принцепса', 'author': 'Батчер', 'isbns': ['978-5-389-24421-4'], 'only_isbn': False},),
        EBook(**{'title': 'Фурия Первого консула', 'author': 'Батчер', 'isbns': ['978-5-389-26094-8'], 'only_isbn': False},),

        EBook(**{'title': 'Гроза из преисподней. Луна светит безумцам. Могила в подарок', 'author': 'Батчер', 'isbns': ['978-5-389-19143-3'], 'only_isbn': False},),
        EBook(**{'title': 'Летний рыцарь. Лики смерти', 'author': 'Батчер', 'isbns': ['978-5-389-19146-4'], 'only_isbn': False},),
        EBook(**{'title': 'Кровавые ритуалы. Барабаны зомби', 'author': 'Батчер', 'isbns': ['978-5-389-19149-5'], 'only_isbn': False},),
        EBook(**{'title': 'Доказательства вины. Белая ночь', 'author': 'Батчер', 'isbns': ['978-5-389-20882-7'], 'only_isbn': False},),
        EBook(**{'title': 'Маленькое одолжение. Продажная шкура', 'author': 'Батчер', 'isbns': ['978-5-389-21273-2'], 'only_isbn': False},),
        EBook(**{'title': 'Перемены. Адская работенка', 'author': 'Батчер', 'isbns': ['978-5-389-22346-2'], 'only_isbn': False},),
        EBook(**{'title': 'История призрака. Холодные дни', 'author': 'Батчер', 'isbns': ['978-5-389-22690-6'], 'only_isbn': False},),
        EBook(**{'title': 'Грязная игра. Правила чародейства', 'author': 'Батчер', 'isbns': ['978-5-389-23608-0'], 'only_isbn': False},),
        EBook(**{'title': 'Ведьмин час', 'author': 'Батчер', 'isbns': ['978-5-389-23643-1'], 'only_isbn': False},),
        EBook(**{'title': 'Поле боя', 'author': 'Батчер', 'isbns': ['978-5-389-24260-9'], 'only_isbn': False},),

        EBook(**{'title': 'Украденный трон. Призыв. Маска призрака', 'author': 'Гейдер', 'isbns': ['978-5-389-19770-1'], 'only_isbn': False},),

        EBook("Новый Дозор", "Лукьяненко", ['978-5-271-41900-3', '978-5-17-118480-3']),
        EBook("Шестой Дозор", "Лукьяненко", ['978-5-17-088817-7', '978-5-17-118536-7']),

        # EBook(**{'title': 'Только ты можешь спасти человечество', 'author': 'Пратчетт', 'isbns': ['978-5-699-33519-0'], 'only_isbn': False},),
        # EBook(**{'title': 'Джонни и мертвецы', 'author': 'Пратчетт', 'isbns': ['978-5-699-33898-6'], 'only_isbn': False},),
        # EBook(**{'title': 'Джонни и бомба', 'author': 'Пратчетт', 'isbns': ['978-5-699-34451-2'], 'only_isbn': False},),
        EBook(**{'title': 'Финт', 'author': 'Пратчетт', 'isbns': ['978-5-699-84214-8'], 'only_isbn': False},),
        # EBook(**{'title': 'Угонщики', 'author': 'Пратчетт', 'isbns': ['978-5-699-31259-7'], 'only_isbn': False},),
        # EBook(**{'title': 'Землекопы', 'author': 'Пратчетт', 'isbns': ['978-5-699-31257-3'], 'only_isbn': False},),
        # EBook(**{'title': 'Крылья', 'author': 'Пратчетт', 'isbns': ['978-5-699-31263-4'], 'only_isbn': False},),
        EBook(**{'title': 'Страта', 'author': 'Пратчетт', 'isbns': ['978-5-889-23131-8', '978-5-699-23137-9'], 'only_isbn': False},),
        EBook(**{'title': 'Народ, или Когда-то мы были дельфинами', 'author': 'Пратчетт', 'isbns': ['978-5-699-42326-2', '978-5-04-119664-6'], 'only_isbn': False},),

        EBook(**{'title': 'Волки Кальи+', 'author': 'Кинг', 'isbns': ['978-5-17-133881-7'], 'only_isbn': False}),
        EBook(**{'title': 'Песнь Сюзанны+', 'author': 'Кинг', 'isbns': ['978-5-17-133029-3'], 'only_isbn': False}),

        EBook(**{'title': 'Душа Бога', 'author': 'Перумов', 'isbns': ['978-5-04-110924-0'], 'only_isbn': False}),

        # EBook(**{'title': '', 'author': '', 'isbns': [], 'only_isbn': False},),
        ] )

    # books = [
    #     # EBook("Ключ из желтого металла", "Фрай"),
    #     # EBook("Преступление и наказание", "Достоевский"), 
    #     # EBook(**{'title': 'Башня ярости. Всходы ветра', 'author': 'Камша', 'isbns': None, 'only_isbn': False}),
    #     EBook(**{'title': 'Волки Кальи+', 'author': 'Кинг', 'isbns': ['978-5-17-133881-7'], 'only_isbn': False}),
    #     # EBook(**),
    #     ]

    # books = [EBook("Преступление и наказание", "Достоевский")]
    # books = [EBook(**{'title': 'Горменгаст', 'author': 'Пик', 'isbns': [], 'only_isbn': False})]


    run(books=books, headless = True)
    
    for b in books:
        b.sort_by_price()
        text = f"{b.get_search_text()}: {len(b.prices)}\n"
        with open(f"./logs/resutls_{time_start}.txt", 'a', encoding="utf8") as file:
            file.write(text)
            for p in b.prices:
                file.write(f"{p.price}: {p.get_url()} ({p.type_search})\n")
            file.write(f"\n")

    print(time_start)
    print(dt.now().strftime("%Y-%m-%d %H-%M"))

    save_objects("./tmp/data.pkl", books)

    for b in books:
        b.optimize_stores_by_cover()
        # b.save_covers(alt_path = True)
    print(dt.now().strftime("%Y-%m-%d %H-%M"))
    save_objects("./tmp/data_opt.pkl", books)
    render_html_page(books)

if __name__  == '__main__':
    main()