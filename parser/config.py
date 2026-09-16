from dataclasses import dataclass, field
from typing import Callable, Any

from parser.utils import _noop

@dataclass
class ParserConfig():
    def get_max_depth(self, item_in_block):
        if item_in_block == 0:
            return self.element_limit
        return int(-(-(self.element_limit/item_in_block) // 1))

    store: str = field(default="")
    base_url: str = field(default="")
    isbn_prefix: bool = field(default=False)
    isbn_escaping_dash: bool = field(default=False) # экранируем тире в isbn
    
    skip_scroll: bool = field(default=False) # engine.scroll_to_last 
    should_continue_on_empty: bool = field(default=False) # engine.run_parser, запускать для магазина если результатов 0
    should_screen_on_empty: bool = field(default=False) # engine.run_parser, для магазина если результатов 0

    wait_for_load_stat: str = field(default=None)
    wait_for_load_time: int = field(default=500)

    fn_extra_goto: Callable[[Any], None] = field(default=_noop) # для дополнения или замены урл
    # fn_click_author: Callable[[Any], None] = field(default=_noop) # выбор автора ВНИМАНИЕ! в проге должно запускаться ДО fn_noresults
    fn_extra_wait_cat: Callable[[Any], None] = field(default=_noop) # для доп ожидания
    fn_noresults: Callable[[Any], bool] = field(default=_noop) # True если страница уведомляет о отсутвии результатов
    fn_login: Callable[[Any], None] = field(default=_noop) # переключение валюты
    fn_currency: Callable[[Any], None] = field(default=_noop) # переключение валюты
    fn_city: Callable[[Any], None] = field(default=_noop) # выбор города

    fn_detect_antibot: Callable[[Any], bool] = field(default=_noop)  # True, если поймали антибот-страниц
    fn_get_antibot_wait_time: Callable[[Any], bool] = field(default=_noop) 
    # Возвращает время ожидания в мс, специфичное для магазина. 
    # Если магазин не может определить точное время — возвращает разумный дефолт сам.

    get_card_locator: Callable[[Any], Any] = field(default=_noop)
    get_nextpage_locator: Callable[[Any], Any] = field(default=_noop)
    element_limit: int = field(default=250)
    generator_cards: Callable[[Any], Any] = field(default=_noop)

    get_card_title: Callable[[Any], str] = field(default=_noop)
    get_card_price: Callable[[Any], str] = field(default=_noop)
    get_card_article: Callable[[Any], str] = field(default=_noop)
    get_card_cover: Callable[[Any], str] = field(default=_noop)
    