import shared.env

from parser.domain import EBook, ShopCard
from z_test_books import regular_books, extra_books_1, extra_books_2, all_book
from saveloads import save_objects
from html_generator import render_html_page

from shutil import rmtree
import os, sys
from datetime import datetime as dt
from parser import run
from shared.paths import rm_log_files
from shared.paths import TMP_DIR

def __run__(books: EBook|list[EBook], headless: bool = True, persistent_context: bool = True, save_res = True, is_test = False):
    rm_log_files()

    time_start = dt.now().strftime("%Y-%m-%d %H-%M")

    run(books=books, headless = headless, persistent_context = persistent_context)

    print(time_start)
    print(dt.now().strftime("%Y-%m-%d %H-%M"))

    if is_test:
        return

    for b in books:
        b.sort_by_price()

    if save_res:
        save_objects(TMP_DIR/"data.pkl", books)
        render_html_page(books, "index_full")

    for b in books:
        if len(b.prices) > 250:
            continue
        b.optimize_stores_by_cover(from_covers_per_store = 0)
    print(dt.now().strftime("%Y-%m-%d %H-%M"))

    if save_res:
        save_objects(TMP_DIR/"data_opt.pkl", books)
        render_html_page(books)

def run_regular():
    books = [EBook(**book) for book in regular_books]
    __run__(books=books)

def run_custom_list(list_book: list = all_book):
    books = [EBook(**book) for book in list_book]
    __run__(books=books, headless = True)

def run_short_test(headless = False):
    # тестовый список: одна книга, которая почти всегда в наличии, остальные опционально
    books = [
        EBook(**{'title': 'Три мушкетера', 'author': 'Дюма', 'isbns': ['978-5-389-19881-4'], 'only_isbn': False}),
        EBook(**{'title': 'Влад Талтош', 'author': 'Браст', 'isbns': ["978-5-04-211206-5"], 'only_isbn': True}), 
        ]
    __run__(books = books, headless = headless, is_test = True)

def main():
    run_regular()

if __name__  == '__main__':
    main()