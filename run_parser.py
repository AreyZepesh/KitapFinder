from parser.domain import EBook, ShopCard
from z_test_books import all_books
from saveloads import save_objects
from html_generator import render_html_page

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
        books.append(EBook(**book))
   
    # books = [
    #     # EBook(**{'title': '', 'author': '', 'isbns': [], 'only_isbn': False},),
    #     EBook("Ключ из желтого металла", "Фрай"),
    #     EBook("Преступление и наказание", "Достоевский"), 
    #     ]
    # books = [EBook(**{'title': 'Ведьма. Матерь Тьмы', 'author': 'Лейбер', 'isbns': [], 'only_isbn': False},)]

    headless = True
    persistent_context = True

    # persistent_context = False
    
    # books = [books[0]]
    # headless = False
    
    run(books=books, headless = headless, persistent_context = persistent_context)
    for b in books:
        b.sort_by_price()

    print(time_start)
    print(dt.now().strftime("%Y-%m-%d %H-%M"))

    save_objects("./tmp/data.pkl", books)
    render_html_page(books, "index_full")

    # if sys.platform == "win32":
    for b in books:
        if len(b.prices) > 250:
            continue
        b.optimize_stores_by_cover(from_covers_per_store = 0)
        # b.save_covers(alt_path = True)
    print(dt.now().strftime("%Y-%m-%d %H-%M"))
    save_objects("./tmp/data_opt.pkl", books)

    render_html_page(books)

if __name__  == '__main__':
    main()