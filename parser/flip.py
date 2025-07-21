from .common import (
    async_playwright, expect,
    asyncio, datetime as dt,
    utils,
    EBook, ShopCard,
    scroll_to_last,
    get_search_urls,
    )

async def flip(context, book: EBook) ->  list[ShopCard]:
    """Парсер ozon, принимает контекст и объект книги, возвращает список объектов с 'карточками'"""
    store = 'flip'
    all_items = []
    options = ""
    # options += "filter-a5059=2&" # твердая обложка
    base_url = f"https://www.flip.kz/search?subsection=1&filter-i101=1&order=price.up&{options}search="
    search_urls = get_search_urls(base_url, book)

    page = await context.new_page()

    for url in search_urls:
        try:
            await page.goto(url)
            try:
                await page.wait_for_load_state()
                # await page.wait_for_load_state("networkidle", timeout = 60000)
            except Exception as ex:
                print(f"!!! {ex}")

            noresults = await page.locator("h2#search-not-result").count()
            if noresults > 0:
                continue

            # # Парсим карточки товаров, сперва получаем "каталог"
            cat = page.locator('div.new-product')
            # # Ищем последний элемент на странице, 
            await scroll_to_last(cat)
 
            # Католог прогружен, получаем все элементы и обходим по одному,
            # что по названию не подходит - пропускаем
            cat = await cat.all()
            for card in cat:
                card_title = await card.locator("div.title").first.inner_text()
                if book.is_TITLE_in_STR(card_title):
                    price = utils.normalizePrice(
                        ( await card.locator("div.price" ).first.inner_text() ).split("₸")[0]
                                                        )
                    article = (await card.get_by_role("link").first.get_attribute("href")).split('=')[-1]
                    screen_file = f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}/{book.title.replace(":","")}/{store}_{price}_{article}.png"
                    all_items.append(ShopCard(price=price, store=store, article=article, screen_file=screen_file))
                    # # TODO Убрать коммент скриншота
                    await card.screenshot(path=screen_file)

        except Exception as ex:
            with open(f"./logs/_error.txt", 'a', encoding="utf8") as file:
                file.write(url+"\n")
            print(ex)
            # raise ex

    # x = input("send anything") 
    await page.close()
    return all_items