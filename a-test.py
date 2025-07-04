from playwright.async_api import async_playwright, expect
import asyncio
import utils

FIND_NAME = "Преступление и наказание" #"Ключ из желтого металла"
PRICEDCT = {'title': None, 'price': None, 'article_id': None, 'screen_file': None}

async def async_work():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
                    # headless=False,
                    args=[
                    "--start-maximized", 
                    '--disable-blink-features=AutomationControlled',
                    # "--disable-infobars",
                    "--no-sandbox",
                    # "--disable-dev-shm-usage",
                    "--disable-gpu"
                            ]
                                            )
        context = await browser.new_context(
            # Я так понимаю опция ниже оч нужна будет в терминальном запуске
                    viewport={"width": 1600, "height": 900},
                    no_viewport=True,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    locale="ru-RU",
                    timezone_id="Asia/Almaty",
                    # java_script_enabled=True,
                    # device_scale_factor=1,
                    # is_mobile=False,
                                            )
        wblist = await wb(context=context,
            hardCover=True
            )

        print(len(wblist))

        x = input("send anything")

        for w in wblist:
            print(w)

        await browser.close()

async def wb(context, hardCover = False):
    cover = ""
    if hardCover:
        cover = "&f1185=10633"
    URL = f"https://global.wildberries.ru/catalog/0/search.aspx?xsubject=381;3455;3456;5322{cover}&search={FIND_NAME}"
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

    # Парсим карточки товаров
    # Ждем пока появится последний элемент на странице и снова крутим в конец страницы
    
    cat = wbpage.locator('//div[@class="product-card-list"]').get_by_role('article')
    # qw = 0
    # while await cat.count() < 100:
    #     await expect(cat.last).to_be_attached()
    #     await cat.nth(-1).scroll_into_view_if_needed()
    #     # cat = wbpage.locator('//div[@class="product-card-list"]').get_by_role('article')
    #     print(await cat.count(), qw)
    #     qw += 1
    # print(await cat.count(), qw)

    prev_count = 0
    retries = 0
    max_retries = 5

    while retries < max_retries:
        count = await cat.count()
        print(f"Загружено карточек: {count}")
        if count == prev_count:
            retries += 1
        else:
            retries = 0
        prev_count = count
        await cat.nth(count - 1).scroll_into_view_if_needed()
        await wbpage.wait_for_timeout(1000)

    # await wbpage.wait_for_timeout(5000)

    cat = await cat.all()
    all_items = []
    for c in cat:
        # title = await c.locator('xpath=.//span[@class="product-card__name"]').first.inner_text()
        title = await c.locator('span.product-card__name').first.inner_text()
        if utils.isTITLEinSTR(FIND_NAME, title):
            item = PRICEDCT.copy()
            item["title"] = utils.normalizeStr(title)
            item["article_id"] = (await c.get_attribute("id")).replace("c",'')
            item["price"] = utils.normalizePrice(
                (await c.locator('xpath=.//span[@class="price__wrap"]').inner_text()).split("₸")[0]
                                                 )
            item["screen_file"] = f"./tmp/wb_{item["article_id"]}.png"
            all_items.append(item)
        # await c.screenshot(path=item.get("screen_file"))

    return all_items
        
def main():
    asyncio.run(async_work())
    # await wbpage.wait_for_timeout(10000)
    # # Перемотка страницы без привязки к чему либо
    # await wbpage.evaluate("""() => {
    #         window.scrollBy(0, 3000);
    #         return document.body.scrollHeight;
    #     }""")
    
    # await wbpage.wait_for_timeout(5000)

    # await wbpage.screenshot(path='./wb.png')

if __name__  == '__main__':
    main()