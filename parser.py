from playwright.async_api import async_playwright, expect
import asyncio
import utils


FIND_NAME = "Преступление и наказание" 
FIND_NAME = "Ключ из желтого металла"
PRICEDCT = {'title': None, 'price': None, 'article_id': None, 'screen_file': None, 'store': None}

async def async_work():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
                    headless=False,
                    args=[
                    "--start-maximized", 
                    '--disable-blink-features=AutomationControlled',
                    # "--disable-infobars",
                    "--no-sandbox",
                    # "--disable-dev-shm-usage",
                    "--disable-gpu"
                            ]
                                            )
        
        # Контекст задается для все сессии. После некоторые вещи сменить не выйдет. 
        # Например разрешение 1600*900 отлично подходит для wb, а для других? TODO
        context = await browser.new_context(
                    viewport={"width": 1600, "height": 900},
                    no_viewport=True,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    locale="ru-RU",
                    timezone_id="Asia/Almaty",
                    # java_script_enabled=True,
                    # device_scale_factor=1,
                    # is_mobile=False,
                                            )
        
        # Паралельный запуск
        results = await asyncio.gather(
            wb(context=context, 
            #    hardCover=True
               ),
            # ozon(context),
                                    )
        # wblist = results[0]

        # Последовательный запуск
        # wblist = await wb(context=context,
        #     hardCover=True
        #     )


        x = input("send anything")

        for res in results:
            print(len(res))
            for w in res:
                print(w)

        await browser.close()

async def wb(context, 
            #  search_dct: dict = None, 
             hardCover = False,
             ) ->  list[dict]:
    cover = ""
    if hardCover:
        # Работает откровенно плохо, вб иногда отбрасывает соответвующие результаты
        cover = "f1185=10633&"
    onlyBookWB = "xsubject=381;3455;3456;5322&"
    URL = f"https://global.wildberries.ru/catalog/0/search.aspx?{onlyBookWB}{cover}search={FIND_NAME}"
    wbpage = await context.new_page()
    await wbpage.goto(URL)
    # await wbpage.wait_for_load_state("networkidle")

    # Переключаем валюту
    country = wbpage.locator('//span[@data-wba-header-name="Country"]').first
    await expect(country).to_be_attached()
    await country.click()
    kzt = wbpage.locator('//input[@value="KZT"]/parent::label').first
    await expect(kzt).to_be_visible()
    await kzt.click()

    # Парсим карточки товаров, сперва получаем "каталог"
    cat = wbpage.locator('//div[@class="product-card-list"]').get_by_role('article')

    # В отдельную функцию? если буду использовать в других частях
    # Крутим к последнему элементу, если 5 раз колво не изменилось - далее
    prev_count = 0
    retries = 0
    max_retries = 5
    while retries < max_retries:
        count = await cat.count()
        print(f"Загружено карточек: {count}") #TODO log
        if count == prev_count:
            retries += 1
        else:
            retries = 0
        prev_count = count
        await cat.nth(count - 1).scroll_into_view_if_needed()
        await wbpage.wait_for_timeout(1000)

    # Католог прогружен, получаем все элементы и обходим по одному,
    # что по названию не подходит - пропускаем
    cat = await cat.all()
    all_items = []
    for c in cat:
        title = await c.locator('span.product-card__name').first.inner_text()
        if utils.isTITLEinSTR(FIND_NAME, title):
            item = PRICEDCT.copy()
            item["title"] = utils.normalizeStr(title)
            item["article_id"] = (await c.get_attribute("id")).replace("c",'')
            item["price"] = utils.normalizePrice(
                (await c.locator('xpath=.//span[@class="price__wrap"]').inner_text()).split("₸")[0]
                                                 )
            item["screen_file"] = f"./tmp/wb_{item["article_id"]}.png"
            item['store'] = 'WB'
            all_items.append(item)
            # TODO Убрать коммент скриншота
            # await c.screenshot(path=item.get("screen_file"))

    return all_items

# async def ozon(context, hardCover = False):
    # cover = ""
    # if hardCover:
    #     cover = "&f1185=10633"
    # URL = f"https://ozon.kz"
    # ozonpage = await context.new_page()
    # await ozonpage.goto(URL)
    # await ozonpage.wait_for_timeout(5000)
    # await ozonpage.close()

def main():
    asyncio.run(async_work())

if __name__  == '__main__':
    main()