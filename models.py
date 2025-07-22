from dataclasses import dataclass, field, asdict

STORE_URLS= {
    "wb": "https://global.wildberries.ru/catalog/{article}/detail.aspx",
    "ozon": "https://ozon.kz/product/{article}",
    "flip": "https://www.flip.kz/catalog?prod={article}",
    }

@dataclass(order=True)
class ShopCard():
    price: int
    store: str
    article: str = field(compare=False)
    screen_file: str = field(compare=False)
    type_search: str = field(default=None, compare=False)

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

    def sort_by_store(self, reverse: bool = False):
        self.prices = sorted(self.prices, key=lambda b: (b.store, b.price), reverse=reverse)

    def sort_by_price(self, reverse: bool = False):
        self.prices = sorted(self.prices, key=lambda b: b.price, reverse=reverse)

    def add_price(self, card: ShopCard):
        # Вынес нормализацию цены из utils, возможно зря. Ранее нормализовал сразу после парсинга нужного элемента
        if not isinstance(card.price, (int, float)):
            card.price = int("".join(c for c in card.price if  c.isdecimal()))

        for i, self_price in enumerate(self.prices):
            if self_price.store == card.store and self_price.article == card.article:
                if self_price.price > card.price:
                    print("замена цены на меньшую")
                    self.prices[i] = card
                if card.type_search == "isbn" and card.type_search != self_price.type_search:
                    print("замена цены на цену с isbn")
                    self.prices[i] = card
                return
        self.prices.append(card)

    def add_prices(self, data: list[ShopCard]):
        for item in data:
            self.add_price(item)

    def to_dict(self):
        return asdict(self)
    
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

#