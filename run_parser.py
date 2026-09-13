import shared.env

from parser.domain import EBook, ShopCard
from z_test_books import all_books
from saveloads import save_objects
from html_generator import render_html_page

from shutil import rmtree
import os, sys
from datetime import datetime as dt
from parser import run
from shared.paths import rm_log_files
from shared.paths import TMP_DIR


def main():
    rm_log_files()

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

    save_objects(TMP_DIR/"data.pkl", books)
    render_html_page(books, "index_full")

    for b in books:
        if len(b.prices) > 250:
            continue
        b.optimize_stores_by_cover(from_covers_per_store = 0)
        # b.save_covers(alt_path = True)
    print(dt.now().strftime("%Y-%m-%d %H-%M"))
    save_objects(TMP_DIR/"data_opt.pkl", books)

    render_html_page(books)

if __name__  == '__main__':
    main()