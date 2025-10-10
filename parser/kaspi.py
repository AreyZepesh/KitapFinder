from .common import (
    expect,
    EBook, ShopCard, ParserConfig,
    run_parser,
    tqdm,
    )

async def _noresults(page):
    noresults = await page.locator("h1.search-result__title-notfound").count()
    if noresults > 0:
        return True

async def _city(page, error_prefix):
    """Переключаем город или закрываем"""
    try:
        dialog = page.locator('div.current-location__dialog').first
        # await expect(dialog).to_be_attached()
        await page.wait_for_timeout(100)
        if await dialog.count() != 0:
            # tqdm.write(f"Выбор города")
            city = await dialog.locator("a").get_by_text("Павлодар").first.click()
            await page.wait_for_timeout(100)
            await page.locator("html.js").first.click()
        else:
            # tqdm.write("! Город уже норм")
            pass
    except Exception as ex:
        tqdm.write(error_prefix)
        tqdm.write("Ошибка при переключении города:")
        tqdm.write(f"{ex}")
    
async def _card_title(card):
    return await card.locator("a.item-card__name-link").first.inner_text()

async def _card_price(card):
    return ( await card.locator("span.item-card__prices-price" ).first.inner_text() )

async def _card_article(card):
    return await card.get_attribute("data-product-id")

 #TODO photo
async def _card_photo(card, page):
    img_url = await card.locator("img.item-card__image").first.get_attribute("src")
    # input(f"\n\n{img_url}")
    response = await page.request.get(img_url)
    return await response.body()

async def main(context, book: EBook) ->  list[ShopCard]:
    parser_config = ParserConfig(
        store = "kaspi",
        base_url = f"https://kaspi.kz/shop/search/?q=:availableInZone:551010000:category:Books&text=",

        fn_noresults = _noresults, 
        fn_city = _city,

        get_cat_locator = lambda page: page.locator('xpath=//div[@data-product-id]'),

        get_card_title = _card_title, 
        get_card_price = _card_price,
        get_card_article = _card_article,
        get_card_photo = _card_photo, #TODO photo
        )
    return await run_parser(context, book, parser_config)

def _no_only_isbn_urls(base_url, book):
    import copy
    from .common import get_search_urls
    if book.only_isbn:
        book_k = copy.deepcopy(book)
        book_k.only_isbn = False
        search_urls = get_search_urls(base_url, book_k) 
    else:
        search_urls = get_search_urls(base_url, book)
    return search_urls