from .common import (
    expect,
    EBook, ShopCard, ParserConfig,
    run_parser, try_and_log_decor,
    tqdm,
    )

async def _noresults(page):
    noresults = await page.get_by_text("По вашему запросу товаров сейчас нет").count() 
    if "category/knigi-16500" not in page.url or noresults > 0:
        return True

@try_and_log_decor("Переключение валюты", repeats = 3)
async def _currency(page):
    # for x in range(3):
    try:
        if await page.locator(":has-text('₸')").count() > 0:
            # continue
            return
        await page.wait_for_timeout(1000)
        button = page.locator("xpath=//button[contains(@data-widget, 'selectedCurrencyLanguage')]").first
        await expect(button).to_be_attached()
        text = await button.inner_text()

        if "KZT" not in text:
            await button.click()

            widget = page.locator("xpath=//div[contains(@data-widget, 'currencyLanguageSelector')]") #
            await expect(widget).to_be_attached()
            cur_input = widget.get_by_role("combobox").last
            await cur_input.fill("KZT")
            await cur_input.press("Enter")
            await widget.get_by_role("button").click()
        # break
    except Exception as ex:
        await page.reload()
        await page.wait_for_load_state("networkidle")
        raise ex
        # continue
    await page.wait_for_timeout(1000)
    
@try_and_log_decor("Переключение города", repeats = 3)
async def _city(page):
    """Переключаем адрес на озон"""
    # for x in range(3):
    try:
        # Ищем виджет адреса с текстом, запращивающим адрес
        address_bar = page.locator("xpath=//div[contains(@data-widget, 'addressBookBarWeb')]") #
        await expect(address_bar).to_be_attached()
        if await address_bar.locator(":has-text('Укажите адрес')").count() > 0 or await address_bar.locator(":has-text('Уточнить адрес')").count():
            # Кликаем по кнопкам до ввода адреса
            await address_bar.click()
            widget = page.locator("xpath=//div[contains(@data-widget, 'commonAddressBook')]") #
            await expect(widget).to_be_attached()
            await widget.get_by_role("button").click()

            # Переключаемся на виджет ввода. Если по локации определило ближайщий пункт - клик, иначе - ищем
            widget = page.locator("xpath=//div[contains(@data-widget, 'addressEditLayoutWrapper')]") #
            await expect(widget).to_be_attached()
            await page.wait_for_timeout(2000) 
            loc_button = widget.locator("span:has-text('Павлодар, улица Ломова, 154')")
            if await loc_button.count() > 0:
                await loc_button.click()
            else:
                del loc_button
                real_adress = "улица Ломова, 154, Павлодар"
                textarea = widget.get_by_role("textbox")
                await textarea.fill(real_adress)
                await page.wait_for_timeout(100)
                await page.locator(f"span:has-text('{real_adress}')").click()
            await page.wait_for_timeout(100)
            await widget.get_by_role("button", name = 'Заберу отсюда').click()
        # break
    except Exception as ex:
        await page.reload()
        await page.wait_for_load_state("networkidle")
        raise ex
        # continue
    await page.wait_for_timeout(1000)

async def _extra_wait_cat(page):
    await page.wait_for_load_state("networkidle")

async def _card_title(card):
    return await card.locator("xpath=.//a[@href]//span[contains(@class, 'tsBody500Medium')]").first.inner_text(timeout = 3000)

async def _card_price(card):
    return ( await card.locator("xpath=.//span[contains(@class, 'tsHeadline') and not( contains(., '×') or contains(., 'мес') )]" ).first.inner_text() ).split("₸")[0]

async def _card_article(card):
    return (await card.get_by_role("link").first.get_attribute("href")).split('/?')[0].split('-')[-1]

 #TODO photo
async def _card_cover(card, page):
    img_url = await card.locator("img").first.get_attribute("src")
    # input(f"\n\n{img_url}")
    return await page.request.get(img_url)

async def _card_info(card):
    return card.locator("div:has(a)").first

async def main(context, book: EBook) ->  list[ShopCard]:
    parser_config = ParserConfig(
        store = "ozon",
        base_url = "https://ozon.kz/category/knigi-16500/?sorting=price&text=",
        wait_for_load_stat = "networkidle",
        wait_for_load_time = 500,

        fn_noresults = _noresults, 
        fn_currency = _currency,
        fn_city = _city,
        get_cat_locator = lambda page: page.locator('xpath=//div[@data-index and @class]'),
        fn_extra_wait_cat = _extra_wait_cat,

        get_card_title = _card_title, 
        get_card_price = _card_price,
        get_card_article = _card_article,
        get_card_cover = _card_cover, #TODO photo
        get_card_screen = _card_info, #TODO screen

        )
    return await run_parser(context, book, parser_config)
