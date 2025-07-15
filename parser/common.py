# import os, sys
# os.chdir( os.path.abspath( os.path.dirname( os.path.dirname(__file__) ) ) )
# sys.path.append( os.getcwd() )

from playwright.async_api import async_playwright, expect
import asyncio
from datetime import datetime

import utils
from models import EBook, ShopCard

async def scroll_to_last(elem_locator):
        # TODO В отдельную функцию? если буду использовать в других частях
        # Крутим к последнему элементу, если 5 раз колво не изменилось - далее
        prev_count = 0
        retries = 0
        max_retries = 5
        while retries < max_retries:
            count = await elem_locator.count()
            # print(f"Загружено карточек: {count}") # TODO log
            if count == prev_count:
                retries += 1
            else:
                retries = 0
            prev_count = count
            await elem_locator.nth(count - 1).scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            # await wbpage.wait_for_timeout(1000)