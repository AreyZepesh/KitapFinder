from bs4 import BeautifulSoup
from bs4.element import PageElement, Tag
from collections import defaultdict
import base64
from utils import load_objects
from models import ShopCard, EBook
from datetime import datetime as dt

def img_to_data_uri(img_bytes: bytes, mime="image/jpeg") -> str:
    b64 = base64.b64encode(img_bytes).decode("ascii")
    return f"data:{mime};base64,{b64}"

def render_book_table(soup: BeautifulSoup, book: EBook) -> None:
    #TODO привести к единому стилю: 
    # типизировать, или нет переменные 
    # х = append или y.append(x) везде
    if not book.prices:
        return
    
    # раскидываем цены по магазинам
    groups = defaultdict(list)
    for price_card in book.prices:
        groups[price_card.store].append(price_card)
    stores = sorted(list(groups.keys()), key=str.lower, reverse=True)
    # stores = STORE_URLS.keys()
    max_rows = max(len(cards) for cards in groups.values())
    max_columns = len(stores)

    for store in groups:
        # Сортируем по возрастанию цены,
        groups[store].sort(key=lambda b: b.price)

    # иницииурем таблицу
    table = soup.new_tag("table", **{"class": "book-table"})
    # table = soup.body.append( soup.new_tag("table") )
    
    # создаем заголовоки
    thead = table.append( soup.new_tag("thead") )

    tr_title = thead.append(soup.new_tag("tr"))
    thead_th = tr_title.append( soup.new_tag("th", colspan = str(max_columns), **{"class": "book-title"}) )
    thead_th.string = f"{book.title}{' - '+book.author if book.author else ''}"
    #шапка с названиями магазинов

    tr_shops = thead.append( soup.new_tag("tr") )
    for store in stores:
        tr_shops.append( soup.new_tag("th") ).string = f"{store}"
    
    # создаем тело таблицы
    tbody: Tag = table.append( soup.new_tag("tbody") )
    for row_idx in range(max_rows):
        tbody_row: Tag = tbody.append( soup.new_tag("tr") )
        for store in stores:
            cards = groups[store]
            if row_idx < len(cards):
                card: ShopCard = cards[row_idx]
                td_cell: Tag = tbody_row.append( soup.new_tag("td", **{"class": f"cell_card {card.type_search}"}) )
                img = soup.new_tag(
                            "img",
                            src=img_to_data_uri(card.cover_bytes),
                            # style=f"max-height:500px; max-width:{int(1000/max_columns)}px;",
                        )
                a = soup.new_tag("a", href=f'{card.get_url()}', **{"class": f"a_card"})
                a.append(img)
                price_div = a.append( soup.new_tag("div", **{"class": "price"}) ) 
                price_div.string = f"{card.price}" #+ (" (ISBN)" if card.type_search == "isbn" else "")
                td_cell.append(a)
            else:
                tbody_row.append( soup.new_tag("td", **{"class": f"empty"}) )

    soup.body.append(table)
    soup.body.append( soup.new_tag("br") )

def get_style(soup: BeautifulSoup):
    style = soup.new_tag("style")

    style.string = """
        table, th, td 
            {
            border: 1px solid black;
            border-collapse: collapse;
            text-align: center;
            /* 
            padding: 15px;
            border-spacing: 5px; 
            */
            }
        table {width: 100%;}
        th, td {width: 25%;}
        img {max-height:250px; max-width:250px;}
        .isbn {background-color: #A5ECA5;}
        """
    
    style.string = """ 
/* ───────── Общий фон ───────── */
body {
    font-family: "Segoe UI", Roboto, Arial, sans-serif;
    background: linear-gradient(180deg, #f4f7fb, #eef2f7);
    color: #333;
}

/* ───────── Таблица книги ───────── */
.book-table {
    border-collapse: separate;
    border-spacing: 0;
    width: 100%;
    margin: 40px 0;
    background: white;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
}

/* ───────── Заголовки ───────── */
.book-table th,
.book-table td {
    padding: 14px 12px;
    text-align: center;
    vertical-align: top;
}

.book-title {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    font-size: 20px;
    letter-spacing: 0.4px;
}

/* Названия магазинов */
.book-table thead tr:nth-child(2) th {
    background: #f1f4fb;
    font-weight: 600;
    color: #444;
    border-bottom: 2px solid #dde3f0;
}

/* ───────── Карточки ───────── */
.cell_card {
    background: linear-gradient(180deg, #ffffff, #f9fbff);
    border: 1px solid #e3e8f4;
    border-radius: 12px;
    min-width: 190px;
    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease,
        background 0.2s ease;
    position: relative;
}

/* hover эффект */
.cell_card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(102, 126, 234, 0.25);
    background: white;
}

/* ───────── Картинка ───────── */
.cell_card img {
    max-height: 300px;
    max-width: 100%;
    object-fit: contain;
    margin-bottom: 10px;
    filter: drop-shadow(0 4px 6px rgba(0,0,0,0.15));
    position: relative;
    z-index: 1;
}

/* ───────── Ссылка ───────── */
.a_card {
    text-decoration: none;
    color: inherit;
    display: block;
}

/* ───────── Цена ───────── */
.price {
    margin-top: 8px;
    font-size: 18px;
    font-weight: 700;
    color: #4a5bdc;
}

/* подчёркивание при наведении */
.a_card:hover .price {
    text-decoration: underline;
}

/* ───── ISBN карточка ───── */
.cell_card.isbn {
    background: linear-gradient(180deg, #e0ecff, #f6f9ff);
    border: 2px solid #3b82f6;
    box-shadow:
        0 0 0 1px rgba(59,130,246,0.25),
        0 12px 26px rgba(59,130,246,0.25);
    position: relative;
}

/* ───── Бейдж ISBN ───── */
.cell_card.isbn::before {
    content: "ISBN";
    position: absolute;
    top: 10px;
    left: 10px;
    z-index: 10;
    background: #2563eb;
    color: white;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 8px;
    border-radius: 999px;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 10px rgba(37,99,235,0.4);
    pointer-events: none;
}

/* ───── Цена ───── */
.cell_card.isbn .price {
    color: #1e40af;
    font-size: 19px;
}

/* ───── hover ───── */
.cell_card.isbn:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow:
        0 18px 40px rgba(59,130,246,0.45);
}


/* ───────── Пустые ячейки ───────── */
.empty {
    background: repeating-linear-gradient(
        45deg,
        #f5f5f5,
        #f5f5f5 10px,
        #fafafa 10px,
        #fafafa 20px
    );
    color: #bbb;
    font-size: 18px;
}

/* ───────── Адаптив ───────── */
@media (max-width: 1200px) {
    .cell_card {
        min-width: 160px;
    }

    .price {
        font-size: 16px;
    }
}
"""
    
    # Темная тема
    dark_style = """
    @media (prefers-color-scheme: dark) {
    body {
        background: linear-gradient(180deg, #0f172a, #020617);
        color: #e5e7eb;
    }

    .book-table {
        background: #020617;
        box-shadow: 0 12px 30px rgba(0,0,0,0.6);
    }

    .book-table th,
    .book-table td {
        border-color: #1e293b;
    }

    .book-title {
        background: linear-gradient(135deg, #4338ca, #6d28d9);
        color: #f9fafb;
    }

    .book-table thead tr:nth-child(2) th {
        background: #020617;
        color: #c7d2fe;
    }

    .cell_card {
        background: linear-gradient(180deg, #020617, #020617);
        border-color: #1e293b;
    }

    .cell_card:hover {
        box-shadow: 0 10px 30px rgba(99,102,241,0.35);
    }

    .cell_card img {
        filter: brightness(0.9) contrast(1.05);
    }

    .price {
        color: #a5b4fc;
    }

    /* ISBN в тёмной теме */
    .cell_card.isbn {
        background: linear-gradient(180deg, #020617, #020617);
        border-color: #60a5fa;
        box-shadow:
            0 0 0 1px rgba(96,165,250,0.4),
            0 14px 32px rgba(96,165,250,0.45);
    }

    .cell_card.isbn::before {
        background: #1d4ed8;
        box-shadow: 0 6px 14px rgba(29,78,216,0.6);
    }

    .empty {
        background: repeating-linear-gradient(
            45deg,
            #020617,
            #020617 10px,
            #020617 10px,
            #020617 20px
        );
        color: #475569;
    }
}

        """
    
    # style.string += dark_style

    return style

def render_html_page(books: list[EBook], html_filename: str = "index"):
    """Создание """
    # Создаем основу. По идее можно и без head/body
    soup = BeautifulSoup("<!DOCTYPE html><html><head><meta charset='UTF-8'></head><body></body></html>", "html.parser")

    # добавляем заголовок страницы
    soup.head.append( soup.new_tag("title") ).string =f"{dt.now().strftime("%Y-%m-%d %H-%M")}"

    # добавить css
    soup.head.append(get_style(soup))

    for book in books:
        render_book_table(soup, book)

    # сохраняем в файл
    with open(f"./output/{html_filename}.html", "w", encoding="utf-8") as file:
        file.write(soup.prettify())

def main():
    # грузим книжки из списка
    books = load_objects("./tmp/data_opt.pkl")
    render_html_page(books)

if __name__  == '__main__':
    main()