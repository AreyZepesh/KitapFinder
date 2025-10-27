from .common import (
    expect,
    EBook, ShopCard, ParserConfig,
    run_parser,
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
    
async def _currency(page, error_prefix):
    """Переключаем валюту"""
    # TODO: потестить с единичным исполнением и сохранением статус в контексте
    try:
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
    except Exception as ex:
        tqdm.write(f"{error_prefix} Ошибка при переключении валюты:")
        tqdm.write(f"{ex}")

async def _card_title(card):
    return await card.locator('span.product-card__name').first.inner_text()

async def _card_price(card):
    return (await card.locator('xpath=.//span[@class="price__wrap"]').inner_text()).split("₸")[0]

async def _card_article(card):
    return (await card.get_attribute("id")).replace("c",'')

 #TODO photo
async def _card_photo(card, page):
    img_url = await card.locator("img.j-thumbnail").first.get_attribute("src")
    # input(f"\n\n{img_url}")
    response = await page.request.get(img_url)
    return response
    content_type = response.headers.get("content-type", "").lower()

    if not content_type.startswith("image/"):
        # Можно логировать или сохранять ошибку
        tqdm.write(f"[WARN] Некорректный контент: {content_type} — {img_url}")
        return None

    # Проверяем статус
    if not response.ok:
        tqdm.write(f"[WARN] Ошибка загрузки: {response.status} — {img_url}")
        return None
    
    return await response.body()


async def main(context, book: EBook) ->  list[ShopCard]:
    parser_config = ParserConfig(
        store = "WB",
        base_url = "https://global.wildberries.ru/catalog/0/search.aspx?search=книга ",
        wait_for_load_time = 1000,

        fn_extra_goto = _extra_urls,
        fn_noresults = _noresults, 
        fn_currency = _currency,

        get_cat_locator = lambda page: page.locator('//div[@class="product-card-list"]').get_by_role('article'),

        get_card_title = _card_title, 
        get_card_price = _card_price,
        get_card_article = _card_article,
        get_card_photo = _card_photo, #TODO photo
        )
    return await run_parser(context, book, parser_config)