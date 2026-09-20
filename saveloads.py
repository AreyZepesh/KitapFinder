import pickle

def save_objects(path: str, data: list) -> None:
    with open(path, "wb") as file:
        pickle.dump(data, file)
    pass

def load_objects(path: str) -> list:
    with open(path, "rb") as file:
        data = pickle.load(file)
    return data

def save_to_file(data, path):
        with open(path, "w", encoding="utf8") as f:
            f.write(data)