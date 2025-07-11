from .common import (
    async_playwright, expect,
    asyncio, 
    utils,
    EBook, ShopCard,
    scroll_to_last,
    )

async def _wb_currency(page):
    """Переключаем валюту"""
    # await page.goto(base_url)
    try:
        country = page.locator('//span[@data-wba-header-name="Country"]').first
        await expect(country).to_be_attached()
        await page.wait_for_timeout(100)
        if await country.inner_text() != "KZT":
            print(f"Меняю валюту: |{await country.inner_text()}|")
            await country.click()
            kzt = page.locator('//input[@value="KZT"]/parent::label').first
            await expect(kzt).to_be_attached()
            await kzt.click()
            await page.wait_for_timeout(1500)
        else:
            # print("! Валюта уже норм")
            pass
    except Exception as ex:
        print("!!! Ошибка при переключении валюты:")
        print(ex)

async def wb(context, book: EBook) ->  list[ShopCard]:

    store = 'WB'
    all_items = []

    onlyBookWB = "xsubject=381;3455;3456;5322&"
    # nocorrection = "nocorrection=1&"
    base_url = f"https://global.wildberries.ru/catalog/0/search.aspx?{onlyBookWB}search="
    search_urls = [base_url+book.get_search_text()]
    if book.isbns:
        for isbn in book.isbns:
            search_urls.append(base_url+isbn)
    #         search_urls.append(base_url+"ISBN/ISSN "+isbn)

    # # TODO test
    for url in search_urls[:]:
        search_urls.append(url.replace(onlyBookWB, ""))
    search_urls.reverse()
    
    page = await context.new_page()

    for url in search_urls:
        try:
            await page.goto(url)
            # await page.wait_for_load_state("networkidle")

            # Парсим карточки товаров, сперва получаем "каталог"
            cat = page.locator('//div[@class="product-card-list"]').get_by_role('article')
            # TODO если нет результатов - ошибка, пример мечи дня и ночи isbs с X
            
            # проверяем и переключаем валюту
            await _wb_currency(page)
            # Ищем последний элемент на странице, 
            await scroll_to_last(cat)

            # TODO убрать: скриншоты начала страницы для отладки
            await cat.nth(0).scroll_into_view_if_needed()
            noc = ""
            if onlyBookWB in url:
                noc = "_book"
            await page.screenshot(path=f"./tmp/{book.title}_{url.split("=")[-1].replace("/", "-").replace(":","")}{noc}.png")

            # Католог прогружен, получаем все элементы и обходим по одному,
            # что по названию не подходит - пропускаем
            cat = await cat.all()
            for card in cat:
                card_title = await card.locator('span.product-card__name').first.inner_text()
                if book.is_TITLE_in_STR(card_title):
                    price = utils.normalizePrice(
                        (await card.locator('xpath=.//span[@class="price__wrap"]').inner_text()).split("₸")[0]
                                                        )
                    article = (await card.get_attribute("id")).replace("c",'')
                    screen_file = f"./tmp/{book.title.replace(":","")}/wb_{article}.png"
                    all_items.append(ShopCard(price=price, store=store, article=article, screen_file=screen_file))
                    # TODO Убрать коммент скриншота
                    await card.screenshot(path=screen_file)

        except Exception as ex:
            with open(f"./tmp/_error.txt", 'a', encoding="utf8") as file:
                file.write(url+"\n")
            print(ex)

    # x = input("send anything") 
    await page.close()
    return all_items