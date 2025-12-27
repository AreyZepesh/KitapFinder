from .common import (
    expect, Page,
    BrowserContext, Locator, APIResponse,
    EBook, ShopCard, ParserConfig,
    run_parser, try_and_log_decor, 
    run_parser_test, run_create_context,
    tqdm, ERROR_PREFIX, dt,
    re,
    )

@try_and_log_decor("Проверка на noresult")
async def _noresults(page: Page):
    noresults1 = await page.get_by_text("По вашему запросу товаров сейчас нет").count() 
    noresults2 = await page.get_by_text("Ничего не нашлось").count() 
    noresults = noresults1 + noresults2
    if "category/knigi-16500" not in page.url or noresults > 0 :
        return True

@try_and_log_decor("Нажать 'Войти'", repeats = 3)
async def _login(page: Page) -> bool:
    """Попытка входа в учетную запись, если отработано - возращает True, что значит что надо перейти на предыдущую страницу"""
    if await page.locator('div[data-widget="profileLogo"]').count() == 0:
        login = page.locator('div[data-widget="profileMenuAnonymous"]')
        if await login.count() != 0:
            await login.first.click()
            await page.wait_for_timeout(1000)
            return True
    else:
        return False

@try_and_log_decor("Переключение валюты", repeats = 3)
async def _currency(page: Page):
    # for x in range(3):
    try:
        if await page.locator(":has-text('₸')").count() > 0:
            # continue
            return
        
        await page.wait_for_timeout(1000)
        button = page.locator("xpath=//button[contains(@data-widget, 'selectedCurrencyLanguage')]")
        if await button.count() != 0:
            button = button.first
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
async def _city(page: Page):
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

@try_and_log_decor("Переключение автора", repeats = 3)
async def _click_author(page: Page, author: str = None):
    if author:
        author_block = page.locator('aside > div > div:has(span:has-text("автор"))').locator('div[type="checkboxesFilter"]')
        see_all = author_block.get_by_text( re.compile("Посмотреть все", re.IGNORECASE) )
        if await see_all.count() > 0:
            await see_all.click()
            author_input = author_block.get_by_role("textbox")
            if await author_input.count() > 0:
                await author_input.fill(author)
            await page.wait_for_timeout(500)
        authors_boxes = author_block.locator("span.tsBody500Medium").filter( has_text=(re.compile(author, re.IGNORECASE)) )
        for box in await authors_boxes.all():
            await box.click()
            await page.wait_for_timeout(500)

        await page.evaluate("window.scrollTo(0, 0)")
        await page.reload()
        return True


async def _gen_cards(page: Page, parser_config: ParserConfig): #TODO вынести deep в конфиг парсера?
    """ Генератор списка локаторов карточек, возвращает locator \n
    card_locator: get_card_locator из парсер конфига \n
    deep: глубина, количество блоков с которых будет собранны данные \n
    """
    @try_and_log_decor("Генератор списка карточек: скролл", repeats = 3)
    async def _page_scroll_to(page: Page, locator_element: Locator = None, mouse_wheel: bool = False):
        if locator_element:
            await locator_element.scroll_into_view_if_needed()

        if mouse_wheel:
            height = await page.evaluate("() => window.innerHeight")
            scroll_to = height * 3
            await page.mouse.wheel(0, scroll_to)
        await page.wait_for_timeout(1000)

    @try_and_log_decor("Генератор списка карточек: получаем артикль", repeats = 3)
    async def _get_last_article(locator_element: Locator, parser_config: ParserConfig):
        return await parser_config.get_card_article(locator_element.last)

    await _extra_wait_cat(page)
    zero_part_css = 'div[data-replace-layout-path]:has(div[data-widget="tileGridDesktop"])'
    # match_block = page.locator(f'div#contentScrollPaginator > div:has({zero_part_css})')

    # ищем блок с карточками, появляющийся при открытии страницы
    # zero_part = match_block.locator(f'{zero_part_css}')
    zero_part = page.locator(f'{zero_part_css}')
    block = parser_config.get_card_locator(zero_part)
    # last_article = await _card_article(block.last)
    # last_article = await _get_last_article(block, parser_config)
    # запоминаем последний артикль блока ↑ и размер блока ↓
    item_in_zero_block = await block.count()
    yield block

    # if last_article == await _get_last_article(block, parser_config):
        # Если последний артикль в блоке не изменился - листаем дальше 
        # Это атавизм, оставщийся со времени скриншотов, так как те прокучивали страницу
    await _page_scroll_to(page, locator_element = block.last)

    # инициализируем переменные: список пройденых индексов, чтобы не повторяться, 
    # количество повторений и максимальная глубина в блоках
    part_indexes = ["-1"]
    retries = 0
    depth = parser_config.get_max_depth(item_in_zero_block)

    while retries < 3 and len(part_indexes) < depth:
        # ищем остальные блоки, кроме первичного
        # not_zero_parts = match_block.locator('div[data-index]:has(div > div[data-widget="tileGridDesktop"])')
        not_zero_parts = page.locator('div[data-index]:has(div > div[data-widget="tileGridDesktop"])')

        if await not_zero_parts.count() > 0:
            # Если имеются, обрабатываем в цикле
            for part in await not_zero_parts.all(): 
                current_index = await part.last.get_attribute('data-index')
                # если индекса в уже пройденных нет - добавляем в пройденные, и обрабатываем блок
                if current_index not in part_indexes:
                    part_indexes.append(current_index)
                    block = parser_config.get_card_locator(part)
                    # last_article = await _get_last_article(block, parser_config)
                    item_in_block = await block.count()
                    yield block

                    # if last_article == await _get_last_article(block, parser_config):
                    # Если последний артикль в блоке не изменился - листаем дальше 
                    # Это атавизм, оставщийся со времени скриншотов, так как те прокучивали страницу
                    await _page_scroll_to(page, locator_element = block.last)

                    # TODO тестить надо
                    # if item_in_block > item_in_zero_block:
                    #     retries = 3
                    # el
                    if item_in_block != item_in_zero_block:
                        retries +=1
                        # if item_in_block == 11:
                        #     retries = 3
                    else:
                        retries = 0
                        
                    break

            else:
                # Если цикл завершился не через брейк, пробуем прокрутиться страницу вниз
                await _page_scroll_to(page, mouse_wheel = True)
                retries +=1
        else: 
            # Если результатов нет, пробуем прокрутиться страницу вниз
            await _page_scroll_to(page, mouse_wheel = True)
            retries +=1
    # else:
    #     tqdm.write(f"{part_indexes}") # TODO для отладки

@try_and_log_decor("Дополнительное ожидание страницы")
async def _extra_wait_cat(page: Page):
    await page.wait_for_load_state("networkidle")

# @try_and_log_decor("Получение тайтла")
async def _card_title(card: Locator):
    return await card.locator("xpath=.//a[@href]//span[contains(@class, 'tsBody500Medium')]").first.inner_text(timeout = 5000)

# @try_and_log_decor("Получение цены")
async def _card_price(card: Locator):
    if await card.get_by_text( re.compile("Нет в наличии", re.IGNORECASE) ).count() == 0:
        return ( await card.locator("xpath=.//span[contains(@class, 'tsHeadline') and not( contains(., '×') or contains(., 'мес') )]" ).first.inner_text(timeout = 5000) ).split("₸")[0]

# @try_and_log_decor("Получение артикля")
async def _card_article(card: Locator):
    return (await card.get_by_role("link").first.get_attribute("href")).split('/?')[0].split('-')[-1]

# @try_and_log_decor("Получение обложки")
async def _card_cover(card: Locator, page) -> APIResponse:
    img_url = await card.locator("img").first.get_attribute("src")
    # input(f"\n\n{img_url}")
    return await page.request.get(img_url)

async def main(context: BrowserContext, book: EBook, alter_search = False, create_context = False) ->  list[ShopCard]:
    base_url = "https://ozon.kz/category/knigi-16500/?text="
    if alter_search:
        base_url = "https://ozon.kz/category/knigi-16500/?sorting=price&text="
    parser_config = ParserConfig(
        store = "ozon",
        base_url = base_url,
        wait_for_load_stat = "networkidle",
        wait_for_load_time = 500,

        fn_noresults = _noresults, 

        fn_login = _login,
        fn_currency = _currency,
        fn_city = _city,
        # fn_click_author = _click_author,

        # fn_extra_wait_cat = _extra_wait_cat,

        get_card_locator = lambda page: page.locator('div[data-widget="tileGridDesktop"] > div[data-index][class][style]'),
        # element_limit = 1000, 
        generator_cards = _gen_cards,

        get_card_title = _card_title, 
        get_card_price = _card_price,
        get_card_article = _card_article,
        get_card_cover = _card_cover, 
        )
    if create_context:
        return await run_create_context(context, parser_config)
    return await run_parser(context, book, parser_config)
