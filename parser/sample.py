from .common import (
    expect,
    EBook, ShopCard, ParserConfig,
    run_parser,
    tqdm,
    )

async def _noresults(page):
    noresults = await page.locator().count()
    if noresults > 0:
        return True    

async def _card_title(card):
    return 

async def _card_price(card):
    return 

async def _card_article(card):
    return 

async def main(context, book: EBook) ->  list[ShopCard]:
    parser_config = ParserConfig(
        store = "",
        base_url = "",
        wait_for_load_stat = "networkidle",
        wait_for_load_time = 1000,

        # fn_extra_goto = _extra_urls,
        fn_noresults = _noresults, 
        # fn_currency = _currency,
        # fn_city = _city,
        get_cat_locator = lambda page: page.locator(),

        get_card_title = _card_title, 
        get_card_price = _card_price,
        get_card_article = _card_article,
        )
    return await run_parser(context, book, parser_config)
    