from .common import (
    async_playwright, expect,
    asyncio, datetime as dt,
    utils,
    EBook, ShopCard,
    scroll_to_last,
    get_search_urls, 
    tqdm,
    )

async def _ozon_currency(page, error_prefix):
    for x in range(3):
        try:
            if await page.locator(":has-text('₸')").count() > 0:
                continue
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
            tqdm.write(error_prefix)
            tqdm.write(f"Ждем выбор валюты ({x+1}/3):")
            tqdm.write(f"{ex}")
            continue
    await page.wait_for_timeout(1000)
    

async def _ozon_city(page, error_prefix):
    """Переключаем адрес на озон"""
    for x in range(3):
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
            break
        except Exception as ex:
            await page.reload()
            await page.wait_for_load_state("networkidle")
            tqdm.write(error_prefix)
            tqdm.write(f"Ждем выбор адреса ({x+1}/3):")
            tqdm.write(f"{ex}")
            continue
    await page.wait_for_timeout(1000)


async def ozon(context, book: EBook) ->  list[ShopCard]:
    """Парсер ozon, принимает контекст и объект книги, возвращает список объектов с 'карточками'"""

    store = 'ozon'
    error_prefix = f"\n{book.title} {store}:"
    all_items = []
    options = ""
    # options += "covertype=537&" # твердая обложка
    base_url = f"https://ozon.kz/category/knigi-16500/?sorting=price&{options}text="
    search_urls = get_search_urls(base_url, book)

    page = await context.new_page()

    for url in search_urls:
        try:
            await page.goto(url[0])
            try:
                # await page.wait_for_load_state()
                # await page.wait_for_timeout(1000)
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(500)
            except Exception as ex:
                tqdm.write(error_prefix)
                tqdm.write("wait load page:")
                tqdm.write(f"{ex}")

            
            noresults = await page.get_by_text("По вашему запросу товаров сейчас нет").count() 
            if "category/knigi-16500" not in page.url or noresults > 0:
                # tqdm.write("!пропуск итерации - нет результатов")
                await page.screenshot(path=f"./logs/_nores/{dt.now().strftime("%Y-%m-%d-%H-%M")}__{book.title.replace(":","")}__{store}.png")
                continue


            # проверяем и переключаем валюту
            await _ozon_currency(page, error_prefix)

            # указываем адрес
            await _ozon_city(page, error_prefix)

            # Парсим карточки товаров, сперва получаем "каталог"
            cat = page.locator('xpath=//div[@data-index and @class]')
            # Ищем последний элемент на странице, 
            await scroll_to_last(cat, ozon_mode=True)
 
            # Каталог прогружен, получаем все элементы и обходим по одному,
            # что по названию не подходит - пропускаем
            cat = await cat.all()
            await page.wait_for_load_state("networkidle")
            for card in cat:
                try:
                    card_title = await card.locator("xpath=.//a[@href]//span[contains(@class, 'tsBody500Medium')]").first.inner_text(timeout = 3000)
                    if book.is_TITLE_in_STR(card_title):
                        price = utils.normalizePrice(
                            ( await card.locator("xpath=.//span[contains(@class, 'tsHeadline') and not( contains(., '×') or contains(., 'мес') )]" ).first.inner_text() ).split("₸")[0]
                                                            )
                        article = (await card.get_by_role("link").first.get_attribute("href")).split('/?')[0].split('-')[-1]
                        screen_file = f"./tmp/SCREEN-{dt.now().strftime("%Y-%m-%d")}/{book.title.replace(":","")}/{store}_{price}_{article}.png"
                        all_items.append(ShopCard(price=price, store=store, article=article, screen_file=screen_file, type_search=url[-1]))
                        # TODO Убрать коммент скриншота
                        await card.screenshot(path=screen_file)
                except Exception as ex:
                    tqdm.write(error_prefix)
                    tqdm.write("Ошибка при обработке одной карточки:")
                    tqdm.write(f"{ex}")

        except Exception as ex:
            with open(f"./logs/_error.txt", 'a', encoding="utf8") as file:
                file.write(url[0]+"\n")
                file.write(f"{ex}\n\n")
            tqdm.write(error_prefix)
            tqdm.write(f"{ex}")
            # input("\n!!! ЖДУ TЫК !!!")

    # TODO del
    # x = input("send anything") 

    await page.close()
    return all_items