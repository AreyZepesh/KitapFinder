from .common import (
    expect, Page,
    BrowserContext, Locator, APIResponse,
    EBook, ShopCard, ParserConfig,
    run_parser, try_and_log_decor, 
    run_parser_test, run_create_context,
    nextpage_gen_cards,
    tqdm, re,
    )

@try_and_log_decor("Проверка на noresult")
async def _noresults(page: Page):
    noresults = await page.locator("h1.search-result__title-notfound").count()
    if noresults > 0:
        return True

@try_and_log_decor("Переключение города")
async def _city(page: Page):
    """Переключаем город или закрываем"""
    dialog = page.locator('div.current-location__dialog').first
    # await expect(dialog).to_be_attached()
    await page.wait_for_timeout(100)
    if await dialog.count() != 0:
        # tqdm.write(f"Выбор города")
        city = await dialog.locator("a").get_by_text("Павлодар").first.click()
        await page.wait_for_timeout(100)
        await page.locator("html.js").first.click()
        await page.wait_for_timeout(500)
    else:
        # tqdm.write("! Город уже норм")
        pass
    
@try_and_log_decor("Переключение автора", repeats = 3)
async def _click_author(page: Page, author: str = None):
    if author:
        author_block = page.locator('div.filters__filter:has(span:has-text("автор"))')
        see_all = author_block.get_by_text( re.compile("Показать еще", re.IGNORECASE) )
        if await see_all.count() > 0:
            await see_all.click()
            await page.wait_for_timeout(200)
        authors_boxes = author_block.locator("div.filters__filter-row  ").filter( has_text=(re.compile(author, re.IGNORECASE)) )
        if await authors_boxes.count() > 0:
            old_url = page.url
            for box in await authors_boxes.all():
                await expect(box).to_be_attached()
                await box.click()
                await page.wait_for_timeout(50)
            await page.wait_for_function(f"() => window.location.href !== '{old_url}'" )
        # await page.wait_for_timeout(500)
        # await page.evaluate("window.scrollTo(0, 0)")
        return True
    
# @try_and_log_decor("Получение тайтла")
async def _card_title(card: Locator):
    return await card.locator("a.item-card__name-link").first.inner_text()

# @try_and_log_decor("Получение цены")
async def _card_price(card: Locator):
    return ( await card.locator("span.item-card__prices-price" ).first.inner_text() )

# @try_and_log_decor("Получение артикля")
async def _card_article(card: Locator):
    return await card.get_attribute("data-product-id")

# @try_and_log_decor("Получение обложки")
async def _card_cover(card: Locator, page: Page) -> APIResponse:
    # input()
    img_url = await card.locator("img.item-card__image").first.get_attribute("src")
    if img_url is None:
        img_url = await card.locator("img.item-card__image").first.get_attribute("data-src")

    try:
        req = await page.request.get(img_url)
        return req
    except Exception as ex:
        ex.add_note(f"URL изображения: {img_url}")
        tqdm.write(f"URL изображения: {img_url}")
        raise ex

# async def _card_info(card: Locator):
#     return card.locator("div.item-card__info").first

async def main(context: BrowserContext, book: EBook, create_context = False) ->  list[ShopCard]:
    parser_config = ParserConfig(
        store = "kaspi",
        base_url = f"https://kaspi.kz/shop/search/?q=:availableInZone:551010000:category:Books&text=",

        fn_noresults = _noresults, 
        fn_city = _city,
        # fn_click_author = _click_author,

        get_card_locator = lambda page: page.locator('xpath=//div[@data-product-id]'),
        get_nextpage_locator = lambda page: page.locator("li.pagination__el:has-text('Следующая'):not(._disabled)"),
        element_limit = 50, # У каспи 12 элементов на страницу, капец медленно станицы грузятся, поэтому ограничиваем количество элементов
        generator_cards = nextpage_gen_cards,

        get_card_title = _card_title, 
        get_card_price = _card_price,
        get_card_article = _card_article,
        get_card_cover = _card_cover, 
        )
    if create_context:
        return await run_create_context(context, parser_config)
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