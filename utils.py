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