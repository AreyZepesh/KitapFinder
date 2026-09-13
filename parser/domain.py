from dataclasses import dataclass, field, asdict
from collections import defaultdict

STORE_URLS= {
    "wb": "https://global.wildberries.ru/catalog/{article}/detail.aspx",
    "ozon": "https://ozon.kz/product/{article}",
    "flip": "https://www.flip.kz/catalog?prod={article}",
    "kaspi": "https://kaspi.kz/shop/p/-{article}",
    }

@dataclass(order=True)
class ShopCard():
    price: int
    store: str
    article: str = field(compare=False)
    type_search: str = field(default=None, compare=False)
    cover_path: str = field(default=None, compare=False)
    cover_bytes: bytes = field(default_factory=bytes, compare=False)

    def to_dict(self):
        return asdict(self)
    
    def get_url(self):
        pattern = STORE_URLS.get(self.store.lower())
        if pattern:
            return pattern.format(article=self.article)
        return
    
    def save_cover(self, alt_path: bool = False):
        from parser.utils import save_image_from_bytes

        path = f"{self.cover_path}-cover"
        if alt_path:
            path = path.replace("SCREEN-", "SCREEN-ALT-")
        save_image_from_bytes(self.cover_bytes, path)
    
@dataclass
class EBook():
    title: str
    author: str = field(default=None)
    isbns: list[str] = field(default_factory=list,)
    only_isbn: bool = field(default=False)
    prices: list[ShopCard] = field(default_factory=list)
    alt_author: str = field(default=None)
    need_check_author: bool = field(default=False) # TODO: возможно на удаление, после тестов 
    # Код из parser.engine.parse_card
    # if book.is_TITLE_in_STR(card_title):
        # if book.need_check_author:
            # card_title = card_title.replace("| Книга б/у", "")
            # if parser_config.store == "ozon" and "|" in card_title:
            #     if book.author and not book.is_AUTHOR_in_STR(card_title):
            #         return 

    def get_search_text(self):
        if self.author:
                return f"{self.title} {self.author}"
        return self.title

    def sort_by_store(self, reverse: bool = False, clean: bool = False):
        if clean:
            self.clean_prices()
        self.prices = sorted(self.prices, key=lambda b: (b.store, b.price), reverse=reverse)

    def sort_by_price(self, reverse: bool = False, clean: bool = False):
        """Сортировка карточек по цене. clean включает clean_prices() до сортировки"""
        if clean:
            self.clean_prices()
        self.prices = sorted(self.prices, key=lambda b: b.price, reverse=reverse)

    def add_price(self, card: ShopCard):
        # Вынес нормализацию цены из utils, возможно зря. Ранее нормализовал сразу после парсинга нужного элемента
        # if not isinstance(card.price, (int, float)):
        #     card.price = int("".join(c for c in card.price if  c.isdecimal()))

        for i, self_price in enumerate(self.prices):
            if self_price.store == card.store and self_price.article == card.article:
                is_new_isbn = card.type_search == "isbn" and self_price.type_search == "text" and self_price.price >= card.price
                if (self_price.price > card.price) or is_new_isbn:
                    self.prices[i] = card
                return

        self.prices.append(card)

    def add_prices(self, data: list[ShopCard]):
        for item in data:
            self.add_price(item)

    def to_dict(self):
        return asdict(self)
    
    def clean_prices(self):
        """Оставляет только карточки с type_search == "isbn", 
        имеющие минимальную цену в рамках одного магазина (store). 
        Все остальные карточки сохраняются без изменений."""
        temp_price = list()
        isbn_by_store = defaultdict(list)
        for p in self.prices: 
            if p.type_search == "isbn":
                isbn_by_store[p.store].append(p)
            else:
                temp_price.append(p)

        for cards in isbn_by_store.values():
            if cards:
                min_price = min(cards).price
                temp_price.extend([card for card in cards if card.price == min_price])
        self.prices = temp_price

    def optimize_stores_by_cover(self, from_covers_per_store = 0):
        from parser.covers import optimize_stores_by_cover
        self.prices = optimize_stores_by_cover(self.prices, from_covers_per_store = from_covers_per_store)
        self.sort_by_price() 

    def save_covers(self, alt_path: bool = False):
        for card in self.prices:
            card.save_cover(alt_path)

    @staticmethod
    def _str_from_comparison(text: str) -> str:
        """Удаляет всё, кроме букв, цифр и пробелов, нормализует регистр"""
        import re
        text = text.replace('ё', 'е').replace('Ё', 'Е')
        text = re.sub(r"[^a-zA-Zа-яА-Я0-9]+", " ", text)
        return text.strip().lower()

    def is_TITLE_in_STR(self, string: str) -> bool:
        """Проверяет, содержится ли заголовок книги в строке.\n\n
        Проверяет вхождение title в string.
        Сперва проверяется наличие title как есть: 
        если является частью string, вернется True.
        Иначе запускается цикл, по слову из title:
        если одного из слов нет string, вернется False;
        иначе, если все слова содержатся в строке, вернется True.
        Я понимаю что такой метод оставляет возможность для ошибки.
        Для фикса этого добавил проверку наличия точки и длины title больше 2"""
        # def save_to_csv(s1,s2,r):
            # import csv
            # with open("./tmp/name.csv", 'a', encoding="utf-8-sig", newline="") as file:
            #     writer = csv.writer(file, delimiter=";")
                # writer.writerow([s1,s2,r])

        norm_title = self._str_from_comparison(self.title)
        norm_string = self._str_from_comparison(string)
        if norm_title in norm_string:
            # save_to_csv(self.title, string, True)
            return True
        if "." in self.title:
            title_words = norm_title.split()
            if len(title_words) > 2:
                for word in title_words: 
                    if word not in norm_string:
                        # save_to_csv(self.title, string, False)
                        return False
                # save_to_csv(self.title, string, True)
                return True
        # save_to_csv(self.title, string, False)
        return False
    
    def is_AUTHOR_in_STR(self, string: str) -> bool:
        """Проверяет, содержится ли автор в строке.\n\n
        Проверяет вхождение author в string.
        Сперва проверяется наличие author как есть: 
        если является частью string, вернется True.
        Иначе запускается цикл, по слову из author:
        если одного из слов есть в string, вернется True;
        Я понимаю что такой метод оставляет возможность для ошибки."""
        norm_author = self._str_from_comparison(self.author)
        norm_string = self._str_from_comparison(string)

        if norm_author in norm_string:
            return True
        if self.alt_author:
            if self._str_from_comparison(self.alt_author) in norm_string:
                return True
        if " " in self.author:
            author_words = norm_author.split()
            for word in author_words: 
                # делаю наоборот от того же с названием: если есть хотя бы одно слова из имени автора - True
                if word in norm_string:
                    return True
        return False


