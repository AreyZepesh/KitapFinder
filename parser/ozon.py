from .common import (
    async_playwright, expect,
    asyncio, datetime as dt,
    utils,
    EBook, ShopCard,
    scroll_to_last,
    get_search_urls,
    )

async def _ozon_currency(page):
    for x in range(3):
        try:
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
            break
        except Exception as ex:
            await page.reload()
            await page.wait_for_load_state("networkidle")
            print("!?", ex)
            continue

async def ozon(context, book: EBook) ->  list[ShopCard]:
    """Парсер ozon, принимает контекст и объект книги, возвращает список объектов с 'карточками'"""

    store = 'ozon'
    all_items = []
    options = ""
    # options += "covertype=537&" # твердая обложка
    base_url = f"https://ozon.kz/category/knigi-16500/?sorting=price&{options}text="
    search_urls = get_search_urls(base_url, book)

    page = await context.new_page()

    for url in search_urls:
        try:
            await page.goto(url[0])
            await page.wait_for_load_state("networkidle")
            
            noresults = await page.get_by_text("По вашему запросу товаров сейчас нет").count() 
            if "category/knigi-16500" not in page.url or noresults > 0:
                # print("!пропуск итерации - нет результатов")
                continue


            # проверяем и переключаем валюту
            await _ozon_currency(page)

            # Парсим карточки товаров, сперва получаем "каталог"
            cat = page.locator('xpath=//div[@data-index and @class]')
            # Ищем последний элемент на странице, 
            await scroll_to_last(cat, ozon_mode=True)
 
            # Католог прогружен, получаем все элементы и обходим по одному,
            # что по названию не подходит - пропускаем
            cat = await cat.all()
            await page.wait_for_load_state("networkidle")
            for card in cat:
                card_title = await card.locator("xpath=.//a[@href]//span[contains(@class, 'tsBody500Medium')]").first.inner_text()
                if book.is_TITLE_in_STR(card_title):
                    price = utils.normalizePrice(
                        ( await card.locator("xpath=.//span[contains(@class, 'tsHeadline')]" ).first.inner_text() ).split("₸")[0]
                                                        )
                    article = (await card.get_by_role("link").first.get_attribute("href")).split('/?')[0].split('-')[-1]
                    screen_file = f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}/{book.title.replace(":","")}/{store}_{price}_{article}.png"
                    all_items.append(ShopCard(price=price, store=store, article=article, screen_file=screen_file, type_search=url[-1]))
                    # TODO Убрать коммент скриншота
                    await card.screenshot(path=screen_file)

        except Exception as ex:
            with open(f"./logs/_error.txt", 'a', encoding="utf8") as file:
                file.write(url[0]+"\n")
            print(ex)

    await page.close()
    return all_items