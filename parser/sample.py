from .common import (
    expect, Page,
    BrowserContext, Locator, APIResponse,
    EBook, ShopCard, ParserConfig,
    run_parser, try_and_log_decor, 
    nextpage_gen_cards,
    tqdm,
    )

@try_and_log_decor("Проверка на noresult")
async def _noresults(page: Page):
    noresults = await page.locator().count()
    if noresults > 0:
        return True    
    
async def _gen_cards(page: Page, parser_config: ParserConfig): 
    """ Генератор списка локаторов карточек, возвращает locator \n
    card_locator: get_card_locator из парсер конфига \n
    deep: глубина, количество блоков с которых будет собранны данные \n
    """
    yield


# @try_and_log_decor("Получение тайтла")
async def _card_title(card: Locator):
    return 

# @try_and_log_decor("Получение цены")
async def _card_price(card: Locator):
    return 

# @try_and_log_decor("Получение артикля")
async def _card_article(card: Locator):
    return 

# @try_and_log_decor("Получение обложки")
async def _card_cover(card: Locator, page: Page) -> APIResponse:
    img_url = await card.locator("img.image").first.get_attribute("src")
    img_url = img_url.replace("//", "http://")
    return await page.request.get(img_url)

async def _card_info(card: Locator):
    return card.locator().first

async def main(context: BrowserContext, book: EBook) ->  list[ShopCard]:
    parser_config = ParserConfig(
        store = "",
        base_url = "",
        wait_for_load_stat = "networkidle",
        wait_for_load_time = 1000,

        # fn_extra_goto = _extra_urls,
        fn_noresults = _noresults, 
        # fn_currency = _currency,
        # fn_city = _city,
        # fn_extra_wait_cat = _extra_wait_cat,
        
        get_card_locator = lambda page: page.locator(),
        get_nextpage_locator = lambda page: page.locator(""),
        generator_cards = nextpage_gen_cards,

        get_card_title = _card_title, 
        get_card_price = _card_price,
        get_card_article = _card_article,
        get_card_cover = _card_cover, #TODO photo
        )
    return await run_parser(context, book, parser_config)
    