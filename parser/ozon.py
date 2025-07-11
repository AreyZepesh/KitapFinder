from .common import (
    async_playwright, expect,
    asyncio, 
    utils,
    EBook, ShopCard,
    scroll_to_last,
    )

# async def ozon(context, hardCover = False):
    # cover = ""
    # if hardCover:
    #     cover = "&f1185=10633"
    # URL = f"https://ozon.kz"
    # ozonpage = await context.new_page()
    # await ozonpage.goto(URL)
    # await ozonpage.wait_for_timeout(5000)
    # await ozonpage.close()