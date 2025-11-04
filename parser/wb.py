from .common import (
    expect,
    EBook, ShopCard, ParserConfig,
    run_parser, try_and_log_decor,
    tqdm,
    )

async def _extra_urls(page):
    # await page.wait_for_timeout(500)
    replaced = await page.locator("a.searching-results__query-replaced").first.is_visible()
    if replaced:
        await page.goto(page.url+"&nocorrection=1")

async def _noresults(page):
    await page.wait_for_timeout(500)
    noresults = await page.locator("div.not-found-search").count()
    if noresults > 0:
        return True
    
@try_and_log_decor("Переключение валюты")
async def _currency(page):
    """Переключаем валюту"""
    country = page.locator('//span[@data-wba-header-name="Country"]').first
    await expect(country).to_be_attached()
    await page.wait_for_timeout(100)
    if await country.inner_text() != "KZT":
        # tqdm.write(f"Меняю валюту: |{await country.inner_text()}|")
        await country.click()
        kzt = page.locator('//input[@value="KZT"]/parent::label').first
        await expect(kzt).to_be_attached()#timeout=20000)
        await kzt.click()
        await page.wait_for_timeout(500)
    else:
        # tqdm.write("! Валюта уже норм")
        pass

@try_and_log_decor("Дополнительное ожидание страницы")
async def _extra_wait_cat(page):
    """Нажимаем кнопку окей, на информации о куках"""
    cookie = page.locator("div.fixed-block__cookies:has(button)")
    if await cookie.count() > 0:
        await cookie.get_by_role("button", name = "Окей").click()
        # cookie.locator("button.cookies__btn btn-minor-md")

async def _card_title(card):
    return await card.locator('span.product-card__name').first.inner_text()

async def _card_price(card):
    return (await card.locator('xpath=.//span[@class="price__wrap"]').inner_text()).split("₸")[0]

async def _card_article(card):
    return (await card.get_attribute("id")).replace("c",'')

 #TODO photo
async def _card_cover(card, page):
    img_url = await card.locator("img.j-thumbnail").first.get_attribute("src")
    # input(f"\n\n{img_url}")
    return await page.request.get(img_url)
    
async def _card_info(card):
    return card.locator("div.product-card__middle-wrap").first

async def main(context, book: EBook) ->  list[ShopCard]:
    parser_config = ParserConfig(
        store = "WB",
        base_url = "https://global.wildberries.ru/catalog/0/search.aspx?search=книга ",
        wait_for_load_time = 1000,

        fn_extra_goto = _extra_urls,
        fn_noresults = _noresults, 
        fn_currency = _currency,

        get_cat_locator = lambda page: page.locator('//div[@class="product-card-list"]').get_by_role('article'),
        fn_extra_wait_cat = _extra_wait_cat,

        get_card_title = _card_title, 
        get_card_price = _card_price,
        get_card_article = _card_article,
        get_card_cover = _card_cover, #TODO photo
        get_card_screen = _card_info, #TODO screen
        )
    return await run_parser(context, book, parser_config)