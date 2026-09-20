def normalizePrice(string: str) -> int:
    """Нормализует цену, делает из строки число"""
    if string:
        return int("".join(c for c in string if  c.isdecimal()))

def save_image_from_bytes(image_bytes, path):
    from PIL import Image
    from io import BytesIO
    from pathlib import Path
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    try:
        # Загружаем байты в объект Image
        img = Image.open(BytesIO(image_bytes))
    except:
        # print("\nОшибка в байтах изображения, не удалось сохранить\n")
        img = Image.new("RGB", (10,10), "#ffffff")
    finally:
        # Сохраняем как PNG
        img.save(f"{path}.png", format="PNG")

def prettify_html(html_content):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.prettify()

def state_filter(data: dict, domain_url: str):
    filtered_cookies = []
    filtered_origins = []
    cookies = data.get("cookies")
    if cookies:
        filtered_cookies = [ 
            c for c in cookies 
            # if is_target( c.get("domain"), domain_url ) 
            if c.get("domain", '').endswith(domain_url)
            or c.get("partitionKey", '').endswith(domain_url) 
                            ]
    origins = data.get("origins")
    if origins:
        filtered_origins = [
            o for o in origins
            # if is_target(o.get("origins"), domain_url)
            if o.get("origins", '').endswith(domain_url)
            ]

    return {
        "cookies": filtered_cookies,
        "origins": filtered_origins
        }

async def _noop(*args, **kwargs):
        """Пустая функция по умолчанию (ничего не делает, no operation)."""
        pass