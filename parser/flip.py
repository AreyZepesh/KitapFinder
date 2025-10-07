from .common import (
    expect,
    EBook, ShopCard, ParserConfig,
    run_parser,
    tqdm,
    )

async def _noresults(page):
    noresults = await page.locator("h2#search-not-result").count()
    if noresults > 0:
        return True
    
async def _card_title(card):
    return await card.locator("div.title").first.inner_text()

async def _card_price(card):
    return ( await card.locator("div.price" ).first.inner_text() ).split("₸")[0]

async def _card_article(card):
    return (await card.locator("a.product[data-event-item-id]").first.get_attribute("data-event-item-id"))

async def main(context, book: EBook) ->  list[ShopCard]:
    parser_config = ParserConfig(
        store = "flip",
        base_url = "https://www.flip.kz/search?subsection=1&filter-i101=1&order=price.up&search=",
        fn_noresults = _noresults, 

        get_cat_locator = lambda page: page.locator('div.new-product'),

        get_card_title = _card_title, 
        get_card_price = _card_price,
        get_card_article = _card_article,
        )
    return await run_parser(context, book, parser_config)