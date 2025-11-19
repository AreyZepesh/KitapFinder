from .common import (
    expect, Page,
    BrowserContext, Locator, APIResponse,
    EBook, ShopCard, ParserConfig,
    run_parser, try_and_log_decor, 
    run_parser_test, 
    nextpage_gen_cards,
    tqdm, re,
    )

@try_and_log_decor("Проверка на noresult")
async def _noresults(page: Page):
    noresults = await page.locator("h2#search-not-result").count()
    if noresults > 0:
        return True
    
@try_and_log_decor("Переключение автора", repeats = 3)
async def _click_author(page: Page, author: str = None):
    if author:
        author_block = page.locator('div[data-filter-field-list-type="peoples"]:not([style="display: none;"])')
        if await author_block.count() > 0:
            await author_block.get_by_role("textbox").fill(author)
            await page.wait_for_timeout(200)
            authors_boxes = author_block.locator("a", has_text=(re.compile(author, re.IGNORECASE)) )
            # tqdm.write(f"{await authors_boxes.count()}")
            for box in await authors_boxes.all():
                await box.click()
                await page.wait_for_timeout(50)
            # input()
            return True

# @try_and_log_decor("Получение тайтла")
async def _card_title(card: Locator):
    return await card.locator("div.title").first.inner_text()

# @try_and_log_decor("Получение цены")
async def _card_price(card: Locator):
    return ( await card.locator("div.price" ).first.inner_text() ).split("₸")[0]

# @try_and_log_decor("Получение артикля")
async def _card_article(card: Locator):
    return (await card.locator("a.product[data-event-item-id]").first.get_attribute("data-event-item-id"))

# @try_and_log_decor("Получение обложки")
async def _card_cover(card: Locator, page: Page) -> APIResponse:
    img_url = await card.locator("img.image").first.get_attribute("src")
    img_url = img_url.replace("//", "http://")
    return await page.request.get(img_url)

# async def _card_info(card: Locator):
#     return card.locator("div.product-data") #.first

async def main(context: BrowserContext, book: EBook, test = False) ->  list[ShopCard]:
    parser_config = ParserConfig(
        store = "flip",
        # base_url = "https://www.flip.kz/search?subsection=1&filter-i101=1&order=price.up&search=", # без листания результаты могут уехать, например Достоевский
        base_url = "https://www.flip.kz/search?subsection=1&filter-i101=1&search=",
        fn_noresults = _noresults, 
        # fn_click_author = _click_author,

        get_card_locator = lambda page: page.locator('div.new-product'),
        get_nextpage_locator = lambda page: page.locator("a[data-page]:has-text('Вперед')"),
        generator_cards = nextpage_gen_cards,


        get_card_title = _card_title, 
        get_card_price = _card_price,
        get_card_article = _card_article,
        get_card_cover = _card_cover,
        )
    if test:
        return await run_parser_test(context, book, parser_config)
    return await run_parser(context, book, parser_config)