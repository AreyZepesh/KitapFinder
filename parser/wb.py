from .common import (
    expect, Page,
    BrowserContext, Locator, APIResponse,
    EBook, ShopCard, ParserConfig,
    run_parser, try_and_log_decor, 
    run_parser_test, run_create_context,
    nextpage_gen_cards,
    tqdm, re, dt, 
    utils,
    )

@try_and_log_decor("Смена url")
async def _extra_urls(page: Page):
    await page.wait_for_timeout(1000)
    replaced = await page.locator("a.searching-results__query-replaced").first.is_visible()
    if replaced:
        await page.goto(page.url+"&nocorrection=1")
    
    await page.wait_for_timeout(200)
    # await page.reload() # часто с первой загрузки данные не корректные, обновление это лечит 

    if replaced:
        return True

@try_and_log_decor("Проверка на noresult")
async def _noresults(page: Page):
    # await page.wait_for_timeout(500)
    noresults = 0
    noresults += await page.locator("div.not-found-search").count()
    noresults += await page.locator("div.not-found-result").count()
    noresults += await page.get_by_text("ничего не нашлось").count()

    if noresults > 0:
        return True
    
@try_and_log_decor("Переключение валюты")
async def _currency(page: Page):
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

@try_and_log_decor("Переключение автора", repeats = 3)
async def _click_author(page: Page, author: str = None):
    async def _see_all_and_fill_text(page: Page, loc: Locator, fill: str):
        see_all = loc.get_by_text( re.compile("Показать все", re.IGNORECASE) )
        if await see_all.count() > 0:
            await see_all.click()
            input_fild = loc.get_by_role("textbox")
            if await input_fild.count() > 0:
                await input_fild.fill(fill)
            # await loc.get_by_role("textbox").fill(fill)
            await page.wait_for_timeout(500)

    async def _click_checkbok_with_text(page: Page, loc: Locator, text: str):
        boxes = loc.locator("div.checkbox-with-text").filter( has_text=(re.compile(text, re.IGNORECASE)) )
        for box in await boxes.all():
            await box.click()
            await page.wait_for_timeout(150)
        else:
            await page.wait_for_timeout(500)

    if author:
        widget = page.locator("div.filters-desktop")
        if await widget.count() == 0:
            all_filter = page.locator('div[data-testid="filters-all"]')
            await expect(all_filter).to_be_attached()
            await all_filter.click()
            await page.wait_for_timeout(100)

        await expect(widget).to_be_attached()

        author_block = widget.locator('div.filters-desktop__item:has(div:has-text("автор"))')
        if await author_block.count() == 0:
            cat_block = widget.locator('div.filters-desktop__item:has(div:has-text("Категория"))')
            await _see_all_and_fill_text(page, cat_block, "книга")
            await _click_checkbok_with_text(page, cat_block, "книга")

            if await author_block.count() == 0:
                # tqdm.write(f"Таки нету автора")
                # input()
                await widget.locator("button.filters-desktop__close").click()
                return
        
        await _see_all_and_fill_text(page, author_block, author)
        await _click_checkbok_with_text(page, author_block, author)

        # Эту часть интегрировал в _noresults, 
        # чтобы если не было результатов заканчивало работу со страницей
        ok = widget.locator('button.filters-desktop__btn-main:not([disabled="disabled"])').filter(has_text=re.compile("Показать", re.IGNORECASE))
        not_ok = widget.get_by_text("Товары не найдены")
        if await ok.count() > 0 or await not_ok.count() == 0:
            await ok.click()
            return True
        else:
            await widget.locator("button.filters-desktop__close").click()
            return "noresults"
            # как то возвращать noresult?
    
async def _gen_cards(page: Page, parser_config: ParserConfig):
    """ Генератор списка локаторов карточек, возвращает locator \n
    Этот возвращает несколько раз, по срезам (сперва 15/30, потом всё после них, и тд)
    Время выполнения на 65 книг было 27:56
    """
    @try_and_log_decor("Генератор списка карточек: скролл", repeats = 3)
    async def _page_scroll_to(page: Page, locator_element: Locator = None, mouse_wheel: bool = False):
        if locator_element:
            await locator_element.scroll_into_view_if_needed()

        if mouse_wheel:
            height = await page.evaluate("() => window.innerHeight")
            scroll_to = height * 3
            await page.mouse.wheel(0, scroll_to)
        await page.wait_for_timeout(200)

    cards_returned = 0
    cards_loaded = 0
    retries = 0
    cards_list: Locator = page.locator('div.product-card-list') 

    # tqdm.write(f"До цикла: {total_cards=} {retries=} {cards_loaded=}")
    while retries < 3 and cards_returned < parser_config.element_limit:
        block = cards_list.locator(f"article[data-card-index]:nth-of-type(n+{cards_returned+1})")
        # Если пытаться отправлять срезы
        # :nth-child(n+16):nth-child(-n+30)
        # :nth-of-type(n+16):nth-of-type(-n+30)
        cards_loaded = await parser_config.get_card_locator(page).count()

        if cards_loaded > cards_returned:
            # tqdm.write(f"Нормальноый ход, крутим до последнего элемента: {cards_returned=} {retries=} {cards_loaded=}")
            retries = 0
            cards_returned = cards_loaded
            await _page_scroll_to(page, locator_element = block.last)
        # elif cards_loaded == 0 or cards_loaded == cards:
        elif cards_loaded == 0 and cards_loaded != cards_returned:
            raise Exception(f"Неожиданная ошибка, сейчас карточек ноль, но недавно было больше: {cards_returned=} {retries=} {cards_loaded=}")
        else:
            retries += 1
            # tqdm.write(f"Вход в ручную прокрутку: {cards_returned=} {retries=} {cards_loaded=}")
            await _page_scroll_to(page, mouse_wheel = True)

        yield block


async def _gen_cards_(page: Page, parser_config: ParserConfig):
    """ Генератор списка локаторов карточек, возвращает locator \n
    Этот возвращает один раз, уже прокрученную страницу
    Время выполнения на 65 книг было 27:54
    """
    @try_and_log_decor("Генератор списка карточек: скролл", repeats = 3)
    async def _page_scroll_to(page: Page, locator_element: Locator = None, mouse_wheel: bool = False):
        if locator_element:
            await locator_element.scroll_into_view_if_needed()

        if mouse_wheel:
            height = await page.evaluate("() => window.innerHeight")
            scroll_to = height * 3
            await page.mouse.wheel(0, scroll_to)
        await page.wait_for_timeout(200)

    cards_returned = 0
    cards_loaded = 0
    retries = 0
    block = parser_config.get_card_locator(page)

    # tqdm.write(f"До цикла: {total_cards=} {retries=} {cards_loaded=}")
    while retries < 3 and cards_returned < parser_config.element_limit:
        cards_loaded = await block.count()

        if cards_loaded > cards_returned:
            # tqdm.write(f"Нормальноый ход, крутим до последнего элемента: {cards_returned=} {retries=} {cards_loaded=}")
            retries = 0
            cards_returned = cards_loaded
            await _page_scroll_to(page, locator_element = block.last)
        # elif cards_loaded == 0 or cards_loaded == cards:
        elif cards_loaded == 0 and cards_loaded != cards_returned:
            raise Exception(f"Неожиданная ошибка, сейчас карточек ноль, но недавно было больше: {cards_returned=} {retries=} {cards_loaded=}")
        else:
            retries += 1
            # tqdm.write(f"Вход в ручную прокрутку: {cards_returned=} {retries=} {cards_loaded=}")
            await _page_scroll_to(page, mouse_wheel = True)

    # else:
    #     tqdm.write(f"while отработал: {cards_returned=} {retries=} {cards_loaded=}")

    yield block

@try_and_log_decor("Дополнительное ожидание страницы", repeats=3)
async def _extra_wait_cat(page: Page):
    # await page.screenshot(path=f"./logs/err/{dt.now().strftime("%Y-%m-%d %H-%M-%S")}.png")
    # with open(f"./logs/err/{dt.now().strftime("%Y-%m-%d %H-%M-%S")}.html", "w", encoding="utf-8-sig") as f:
    #     f.write(utils.prettify_html(await page.content()))
    # await page.wait_for_timeout(1000)
    # await page.screenshot(path=f"./logs/err/{dt.now().strftime("%Y-%m-%d %H-%M-%S")}.png")
    # with open(f"./logs/err/{dt.now().strftime("%Y-%m-%d %H-%M-%S")}.html", "w", encoding="utf-8-sig") as f:
    #     f.write(utils.prettify_html(await page.content()))
    # antibot = await page.get_by_text("Подозрительная активность").count()
    # antibot += await page.get_by_text("подождите").count()
    # tqdm.write(f"{antibot=}")

    # if antibot > 0:
    #     tqdm.write("\nЖдем страницу, так как вылез антибот")
    #     reload_time = await page.locator('meta[http-equiv="refresh"]').first.get_attribute('content')
    #     reload_time = utils.normalizePrice(reload_time)
    #     reload_time += 10
    #     reload_time *= 1000
    #     tqdm.write(f"{reload_time=}ms")

    #     await page.wait_for_timeout(reload_time)
    #     await page.wait_for_load_state()
        
    await expect(page.locator("div.product-card-list")).to_be_attached(
                                                                # timeout=7500
                                                                       )

    cookie = page.locator("div.fixed-block__cookies:has(button)")
    if await cookie.count() > 0:
        await cookie.get_by_role("button", name = "Окей").click()
        # cookie.locator("button.cookies__btn btn-minor-md")

# @try_and_log_decor("Получение тайтла")
async def _card_title(card: Locator):
    return await card.locator('span.product-card__name').first.inner_text()

# @try_and_log_decor("Получение цены")
async def _card_price(card: Locator):
    return (await card.locator('xpath=.//span[@class="price__wrap"]').inner_text()).split("₸")[0]

# @try_and_log_decor("Получение артикля")
async def _card_article(card: Locator):
    return (await card.get_attribute("id")).replace("c",'')

# @try_and_log_decor("Получение обложки")
async def _card_cover(card: Locator, page: Page) -> APIResponse:
    img_url = await card.locator("img.j-thumbnail").first.get_attribute("src")
    # input(f"\n\n{img_url}")
    return await page.request.get(img_url)
    
# async def _card_info(card: Locator):
#     return card.locator("div.product-card__middle-wrap").first

async def main(context: BrowserContext, book: EBook, alter_search = False, create_context = False) ->  list[ShopCard]:
    base_url = "https://global.wildberries.ru/catalog/0/search.aspx?search=книга "
    if alter_search:
        base_url = "https://global.wildberries.ru/catalog/0/search.aspx?search="
    parser_config = ParserConfig(
        store = "WB",
        base_url = base_url,
        isbn_prefix = True,

        wait_for_load_time = 1000,

        fn_extra_goto = _extra_urls,
        fn_extra_wait_cat = _extra_wait_cat,
        fn_noresults = _noresults, 
        fn_currency = _currency,
        
        # get_card_locator = lambda page: page.locator('//div[@class="product-card-list"]').get_by_role('article'),
        get_card_locator = lambda page: page.locator('div.product-card-list > article[data-card-index]'),
        # get_nextpage_locator = lambda page: page.locator("a.pagination-next:has-text('Следующая страница')"),
        # element_limit = 100, 
        generator_cards = _gen_cards,

        get_card_title = _card_title, 
        get_card_price = _card_price,
        get_card_article = _card_article,
        get_card_cover = _card_cover, #TODO photo
        # get_card_screen = _card_info, #TODO screen
        )
    if create_context:
        return await run_create_context(context, parser_config)
    return await run_parser(context, book, parser_config)