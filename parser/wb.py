from .common import (
    async_playwright, expect,
    asyncio, datetime as dt,
    utils,
    EBook, ShopCard,
    scroll_to_last, 
    get_search_urls,
    )

async def _wb_currency(page):
    """Переключаем валюту"""
    # TODO: потестить с единичным исполнением и сохранением статус в контексте
    try:
        country = page.locator('//span[@data-wba-header-name="Country"]').first
        await expect(country).to_be_attached()
        await page.wait_for_timeout(100)
        if await country.inner_text() != "KZT":
            # print(f"Меняю валюту: |{await country.inner_text()}|")
            await country.click()
            kzt = page.locator('//input[@value="KZT"]/parent::label').first
            await expect(kzt).to_be_attached(timeout=20000)
            await kzt.click()
            await page.wait_for_timeout(500)
        else:
            # print("! Валюта уже норм")
            pass
    except Exception as ex:
        print("!!! Ошибка при переключении валюты:")
        print(ex)

async def _create_search_context(page, url):
    """Попытка создать контекст поиска, низкая эффективность"""
    await page.goto(url+"книги")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(1000)
    await page.goto(url+"преступление и наказание")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(1000)
    # page.context.my_data = {"wb" : True}

async def wb(context, book: EBook) ->  list[ShopCard]:
    """Парсер wildberries, принимает контекст и объект книги, возвращает список объектов с 'карточками'"""
    store = 'WB'
    all_items = []
    options = ""
    # options += "xsubject=381;3455;3456;5322&" #только ру книги 
    base_url = f"https://global.wildberries.ru/catalog/0/search.aspx?{options}search=книга "
    search_urls = get_search_urls(base_url, book)

    # TODO проверку на предложение других результатов и тогда поиск с nocorrection=1&
    # затычка для поиска результатов без коррекции запроса, например понадовилось на 
    # https://global.wildberries.ru/catalog/0/search.aspx?search=книга Держи марку! Пратчетт
    base_url = f"https://global.wildberries.ru/catalog/0/search.aspx?nocorrection=1&{options}search=книга "
    search_urls.extend( get_search_urls(base_url, book) )
    
    page = await context.new_page()

    for url in search_urls:
        try:
            await page.goto(url[0])
            try:
                await page.wait_for_load_state()
                await page.wait_for_timeout(500)
                # await page.wait_for_load_state("networkidle", timeout = 60000)
            except Exception as ex:
                print(f"!!! {ex}")

            noresults = await page.locator("div.not-found-result").count()
            if noresults > 0:
                # print("!пропуск итерации - нет результатов")
                continue

            # проверяем и переключаем валюту
            await _wb_currency(page)

            # Парсим карточки товаров, сперва получаем "каталог"
            cat = page.locator('//div[@class="product-card-list"]').get_by_role('article')
            # Ищем последний элемент на странице, 
            await scroll_to_last(cat)

            # Каталог прогружен, получаем все элементы и обходим по одному,
            # что по названию не подходит - пропускаем
            cat = await cat.all()
            for card in cat:
                card_title = await card.locator('span.product-card__name').first.inner_text()
                if book.is_TITLE_in_STR(card_title):
                    price = utils.normalizePrice(
                        (await card.locator('xpath=.//span[@class="price__wrap"]').inner_text()).split("₸")[0]
                                                        )
                    article = (await card.get_attribute("id")).replace("c",'')
                    screen_file = f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}/{book.title.replace(":","")}/{store}_{price}_{article}.png"
                    all_items.append(ShopCard(price=price, store=store, article=article, screen_file=screen_file, type_search=url[-1]))
                    # TODO Убрать коммент скриншота
                    await card.screenshot(path=screen_file)

        except Exception as ex:
            with open(f"./logs/_error.txt", 'a', encoding="utf8") as file:
                file.write(url[0]+"\n")
            print(ex)

    # TODO del
    # x = input("send anything") 

    await page.close()
    return all_items