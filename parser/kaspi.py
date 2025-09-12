from .common import (
    async_playwright, expect,
    asyncio, datetime as dt,
    utils,
    EBook, ShopCard,
    scroll_to_last,
    get_search_urls,
    )
import copy

async def _kaspi_city(page):
    """Переключаем город или закрываем"""
    try:
        dialog = page.locator('div.current-location__dialog').first
        # await expect(dialog).to_be_attached()
        await page.wait_for_timeout(100)
        if await dialog.count() != 0:
            # print(f"Выбор города")
            city = await dialog.locator("a").get_by_text("Павлодар").first.click()
            await page.wait_for_timeout(100)
            await page.locator("html.js").first.click()
        else:
            # print("! Город уже норм")
            pass
    except Exception as ex:
        # print("!!! Ошибка при переключении города:")
        print(ex)

async def kaspi(context, book: EBook) ->  list[ShopCard]:
    """Парсер ozon, принимает контекст и объект книги, возвращает список объектов с 'карточками'"""
    store = 'kaspi'
    all_items = []
    base_url = f"https://kaspi.kz/shop/search/?q=:availableInZone:551010000:category:Books&text="
    ""

    # TODO затычка, так как на каспи очень мало иcбн,
    # до этого было только то, что в else
    if book.only_isbn:
        book_k = copy.deepcopy(book)
        book_k.only_isbn = False
        search_urls = get_search_urls(base_url, book_k) 
    else:
        search_urls = get_search_urls(base_url, book)
    # search_urls = get_search_urls(base_url, book)

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

            await _kaspi_city(page)

            noresults = await page.locator("h1.search-result__title-notfound").count()
            if noresults > 0:
                # print("Нет результата")
                continue


            # Парсим карточки товаров, сперва получаем "каталог"
            cat = page.locator('xpath=//div[@data-product-id]')
            await page.wait_for_timeout(500)

            # Ищем последний элемент на странице, 
            await scroll_to_last(cat)
 
            # Каталог прогружен, получаем все элементы и обходим по одному,
            # что по названию не подходит - пропускаем
            cat = await cat.all()
            for card in cat:
                await card.focus()
                card_title = await card.locator("a.item-card__name-link").first.inner_text()
                if book.is_TITLE_in_STR(card_title):
                    price = utils.normalizePrice(
                        ( await card.locator("div.item-card__debet " ).first.inner_text() )
                                                        )
                    article = await card.get_attribute("data-product-id")
                    screen_file = f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}/{book.title.replace(":","")}/{store}_{price}_{article}.png"
                    all_items.append(ShopCard(price=price, store=store, article=article, screen_file=screen_file, type_search=url[-1]))
                    # # TODO Убрать коммент скриншота
                    await card.screenshot(path=screen_file)

        except Exception as ex:
            with open(f"./logs/_error.txt", 'a', encoding="utf8") as file:
                file.write(url[0]+"\n")
            print(ex)
            # raise ex

    # x = input("send anything") 
    await page.close()
    return all_items