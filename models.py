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
    screen_file: str = field(compare=False)
    type_search: str = field(default=None, compare=False)
    # photo_bytes: bytes = field(default_factory=bytes, compare=False) #TODO photo
    cover_bytes: bytes = field(default_factory=bytes, compare=False) #TODO photo
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
    
@dataclass
class EBook():
    title: str
    author: str = field(default=None)
    isbns: list[str] = field(default_factory=list,)
    only_isbn: bool = field(default=False)
    prices: list[ShopCard] = field(default_factory=list)

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

    def optimize_stores_by_cover(self):
        from services.ebook_services import optimize_stores_by_cover
        self.prices = optimize_stores_by_cover(self.prices)
        self.sort_by_price() 

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
        norm_title = self._str_from_comparison(self.title)
        norm_string = self._str_from_comparison(string)
        if norm_title in norm_string:
            return True
        if "." in self.title:
            title_words = norm_title.split()
            if len(title_words) > 2:
                for word in title_words: 
                    if word not in norm_string:
                        return False
            return True
        return False


@dataclass
class ParserConfig():
    def get(self, key, default = None):
        return getattr(self, key, default)

    @staticmethod
    async def _noop(*args, **kwargs):
        """Пустая функция по умолчанию (ничего не делает, no operation)."""
        pass

    store: str = field(default="")
    base_url: str = field(default="")
    wait_for_load_stat: str = field(default=None)
    wait_for_load_time: int = field(default=500)


    fn_extra_goto: Callable[[Any], None] = field(default=_noop) # для дополнения или замены урл
    fn_noresults: Callable[[Any], bool] = field(default=_noop)
    fn_currency: Callable[[Any], None] = field(default=_noop)
    fn_city: Callable[[Any], None] = field(default=_noop)

    get_cat_locator: Callable[[Any], Any] = field(default=_noop)

    fn_extra_wait_cat: Callable[[Any], None] = field(default=_noop) # для доп ожидания

    get_card_title: Callable[[Any], str] = field(default=_noop)
    get_card_price: Callable[[Any], str] = field(default=_noop)
    get_card_article: Callable[[Any], str] = field(default=_noop)
    get_card_photo: Callable[[Any], str] = field(default=_noop) #TODO photo
    