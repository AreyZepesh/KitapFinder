from .common import (
    expect,
    EBook, ShopCard, ParserConfig,
    run_parser, try_and_log_decor,
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

 #TODO photo
async def _card_cover(card, page):
    img_url = await card.locator("img.image").first.get_attribute("src")
    img_url = img_url.replace("//", "http://")
    return await page.request.get(img_url)

async def _card_info(card):
    return card.locator("div.product-data") #.first

async def main(context, book: EBook) ->  list[ShopCard]:
    parser_config = ParserConfig(
        store = "flip",
        # base_url = "https://www.flip.kz/search?subsection=1&filter-i101=1&order=price.up&search=", # без листания результаты могут уехать, например Достоевский
        base_url = "https://www.flip.kz/search?subsection=1&filter-i101=1&search=",
        fn_noresults = _noresults, 

        get_cat_locator = lambda page: page.locator('div.new-product'),

        get_card_title = _card_title, 
        get_card_price = _card_price,
        get_card_article = _card_article,
        get_card_cover = _card_cover, #TODO photo
        get_card_screen = _card_info, #TODO screen
        )
    return await run_parser(context, book, parser_config)