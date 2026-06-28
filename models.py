from dataclasses import dataclass, field, asdict
from typing import Callable, Any
from collections import defaultdict
from itertools import combinations

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
    # screen_bytes: bytes = field(default_factory=bytes, compare=False) #TODO screen
    # screen_file: Any = field(default=None) # TODO тестовое поле
    # x: Any = field(default=None) # TODO тестовое поле

    # def __str__(self):
    #     return f"\nprice: {self.price}, store: {self.store}, article: {self.article}, url: {self.get_url()}"
    
    # def __repr__(self):
    #     return self.__str__()

    def to_dict(self):
        return asdict(self)
    
    def get_url(self):
        pattern = STORE_URLS.get(self.store.lower())
        if pattern:
            return pattern.format(article=self.article)
        return
    
    def save_cover(self, alt_path: bool = False):
        from utils import save_image_from_bytes

        path = f"{self.cover_path}-cover"
        if alt_path:
            path = path.replace("SCREEN-", "SCREEN-ALT-")
            # TODO так то это для отладки
        save_image_from_bytes(self.cover_bytes, path)
    
@dataclass
class EBook():
    title: str
    author: str = field(default=None)
    isbns: list[str] = field(default_factory=list,)
    only_isbn: bool = field(default=False)
    prices: list[ShopCard] = field(default_factory=list)
    alt_author: str = field(default=None)
    need_check_author: bool = field(default=False)

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
        if not isinstance(card.price, (int, float)):
            card.price = int("".join(c for c in card.price if  c.isdecimal()))

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
        from services.ebook_services import optimize_stores_by_cover
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
            # return True
        # print(f"\n {norm_author} / {norm_string}")
        return False


@dataclass
class ParserConfig():
    def get(self, key, default = None):
        return getattr(self, key, default)
    
    def get_max_depth(self, item_in_block):
        if item_in_block == 0:
            return self.element_limit
        return int(-(-(self.element_limit/item_in_block) // 1))

    @staticmethod
    async def _noop(*args, **kwargs):
        """Пустая функция по умолчанию (ничего не делает, no operation)."""
        pass

    store: str = field(default="")
    base_url: str = field(default="")
    isbn_prefix: bool = field(default=False)
    isbn_escaping_dash: bool = field(default=False)
    # base_url_alt: str = field(default=None)

    wait_for_load_stat: str = field(default=None)
    wait_for_load_time: int = field(default=500)

    fn_extra_goto: Callable[[Any], None] = field(default=_noop) # для дополнения или замены урл
    # fn_click_author: Callable[[Any], None] = field(default=_noop) # выбор автора ВНИМАНИЕ! в проге должно запускаться ДО fn_noresults
    fn_extra_wait_cat: Callable[[Any], None] = field(default=_noop) # для доп ожидания
    fn_noresults: Callable[[Any], bool] = field(default=_noop) # True если страница уведомляет о отсутвии результатов
    fn_login: Callable[[Any], None] = field(default=_noop) # переключение валюты
    fn_currency: Callable[[Any], None] = field(default=_noop) # переключение валюты
    fn_city: Callable[[Any], None] = field(default=_noop) # выбор города


    get_card_locator: Callable[[Any], Any] = field(default=_noop)
    get_nextpage_locator: Callable[[Any], Any] = field(default=_noop)
    element_limit: int = field(default=500)
    # get_max_depth: Callable[[Any], int] = field(default=_get_max_depth)
    generator_cards: Callable[[Any], Any] = field(default=_noop)

    get_card_title: Callable[[Any], str] = field(default=_noop)
    get_card_price: Callable[[Any], str] = field(default=_noop)
    get_card_article: Callable[[Any], str] = field(default=_noop)
    get_card_cover: Callable[[Any], str] = field(default=_noop)
    # get_card_screen: Callable[[Any], str] = field(default=_noop) #TODO screen
    