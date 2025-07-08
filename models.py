from dataclasses import dataclass, field, asdict

STORE_URLS= {
    "wb": "https://global.wildberries.ru/catalog/{article}/detail.aspx",
    "ozon": "https://ozon.kz/product/{article}",
    }

@dataclass(order=True)
class ShopCard():
    price: int
    store: str
    article: str = field(compare=False)
    screen_file: str = field(compare=False)

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
    prices: list[ShopCard] = field(default_factory=list)

    def sort_by_store(self, reverse: bool = False):
        self.prices = sorted(self.prices, key=lambda b: (b.store, b.price), reverse=reverse)

    def sort_by_price(self, reverse: bool = False):
        self.prices = sorted(self.prices, key=lambda b: b.price, reverse=reverse)

    def add_price(self, card: ShopCard):
        for i, p in enumerate(self.prices):
            if p.store == card.store and p.article == card.article:
                if p.price > card.price:
                    self.prices[i] = card
                return
        self.prices.append(card)

    def to_dict(self):
        return asdict(self)

    # def has_price_from(self, store: str, article: str) -> bool:
    #     # TODO Оставлять с минимальной ценой
    #     return any(p.store == store and p.article == article for p in self.prices)

    # def add_price(self, price: int, store: str, article: str, screen_file: str):
    #     if self.has_price_from(store, article):
    #         return
    #     self.prices.append( ShopCard(price = price, 
    #                                 store = store, 
    #                                 article = article, 
    #                                 screen_file = screen_file) )