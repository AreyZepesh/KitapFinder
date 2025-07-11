def normalizeStr(string: str) -> str:
    """Нормализует данные в строке:
     - заменяет табуляции на пробелы
     - убирает лишние пробелы"""
    import re
    string = re.sub(r"[^a-zA-Zа-яёА-ЯЁ0-9,.!'+-–]+", " ", string)
    return string.strip()

def normalizePrice(string: str) -> int:
    """Нормализует цену, делает из строки число"""
    if string:
        return int("".join(c for c in string if  c.isdecimal()))

def strFromComparison(string: str) -> str:
    """Убирает из строки все кроме букв, цифр и пробелов.
    Так же нормализует"""
    import re
    text = text.replace('ё', 'е').replace('Ё', 'Е')
    text = re.sub(r"[^a-zA-Zа-яА-Я0-9]+", " ", text)
    return text.strip().lower()

def isTITLEinSTR(title: str, string: str) -> bool:
    """Проверяет вхождение title в string.
    Сперва проверяется наличие title как есть: 
    если является частью string, вернется True.
    Иначе запускается цикл, по слову из title:
    если одного из слов нет string, вернется False;
    иначе, если все слова содержатся в строке, вернется True.
    Я понимаю что такой метод оставляет возможность для ошибки.
    Для фикса этого добавил проверку наличия точки и длины title больше 2"""
    haveDot = True if "." in title else False
    norm_title = strFromComparison(title)
    norm_string = strFromComparison(string)
    if norm_title in norm_string:
        return True
    if "." in title:
        title_words = norm_title.split()
        if len(title_words) > 2:
            for word in title_words: 
                if word not in norm_string:
                    return False
        return True
    return False

# Куки
def addCookie(driver, file='./tmp/cookies.json'):
    import json
    # куки входа... как долго проживут?
    try:
        with open(file, 'r') as file:
            cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
    except Exception as ex:
        print(ex)
        print("Нету кука?")

def saveCookie(driver, file='./tmp/cookies.json'):
    import json
    with open(file, 'w') as file:
        json.dump(driver.get_cookies(), file)