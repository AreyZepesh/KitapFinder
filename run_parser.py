from models import EBook, ShopCard
from z_test_books import all_books, books_Aizada
from utils import save_objects, save_image_from_bytes
from services.html_generator import render_html_page

from shutil import rmtree
import os, sys
from datetime import datetime as dt
from parser import run

def main():
    if os.path.exists("./logs/_urls.txt"):
        os.remove("./logs/_urls.txt")
    if os.path.exists("./logs/_error.txt"):
        os.remove("./logs/_error.txt")
    if os.path.exists(f"./logs/err"):
        rmtree(f"./logs/err")
    if os.path.exists(f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}"):
        rmtree(f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}")
    if os.path.exists(f"./tmp/SCREEN-ALT-{dt.now().strftime("%Y-%m-%d")}"):
        rmtree(f"./tmp/SCREEN-ALT-{dt.now().strftime("%Y-%m-%d")}")
    if os.path.exists(f"./logs/_nores"):
        rmtree(f"./logs/_nores")
    if os.path.exists(f"./logs/wb"):
        rmtree(f"./logs/wb")
    time_start = dt.now().strftime("%Y-%m-%d %H-%M")

    books = []
    for book in all_books:
    # for book in books_Aizada:
        books.append(EBook(**book))
   
    # books = [
    #     # EBook(**{'title': '', 'author': '', 'isbns': [], 'only_isbn': False},),
    #     EBook("Ключ из желтого металла", "Фрай"),
    #     EBook("Преступление и наказание", "Достоевский"), 
    #     ]

    # books = [EBook("Преступление и наказание", "Достоевский")]
    # books = [EBook("Остров Сахалин", "Чехов", ['978-5-389-28937-6'])]
    # books = [EBook(**{'title': 'Виконт де Бражелон, или Еще десять лет спустя', 'author': 'Дюма', 'isbns': ['978-5-389-24464-1'], 'only_isbn': True},)]
    # books = [EBook(**{'title': 'Террор', 'author': 'Симмонс', 'isbns': [], 'only_isbn': False, 'need_check_author': True},)]
    # books = [books[1]]

    run(books=books, headless = True)
    # <button class="rb" onclick="reload()">Обновить</button>
    for b in books:
        b.sort_by_price()
        text = f"{b.get_search_text()}: {len(b.prices)}\n"
        # with open(f"./logs/resutls_{time_start}.txt", 'a', encoding="utf8") as file:
        #     file.write(text)
        #     for p in b.prices:
        #         file.write(f"{p.price}: {p.get_url()} ({p.type_search})\n")
        #     file.write(f"\n")

    print(time_start)
    print(dt.now().strftime("%Y-%m-%d %H-%M"))

    save_objects("./tmp/data.pkl", books)
    render_html_page(books, "index_full")

    # if sys.platform == "win32":
    for b in books:
        b.optimize_stores_by_cover(from_covers_per_store = 5)
        # b.save_covers(alt_path = True)
    print(dt.now().strftime("%Y-%m-%d %H-%M"))
    save_objects("./tmp/data_opt.pkl", books)

    render_html_page(books)

if __name__  == '__main__':
    main()