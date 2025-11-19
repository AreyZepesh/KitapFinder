import pickle

def normalizePrice(string: str) -> int:
    """Нормализует цену, делает из строки число"""
    if string:
        return int("".join(c for c in string if  c.isdecimal()))

def save_objects(path: str, data: list) -> None:
    with open(path, "wb") as file:
        pickle.dump(data, file)
    pass

def load_objects(path: str) -> list:
    with open(path, "rb") as file:
        data = pickle.load(file)
    return data

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

def save_to_file(data, path):
        with open(path, "w", encoding="utf8") as f:
            f.write(data)

def prettify_html(html_content):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.prettify()