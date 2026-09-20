from dotenv import load_dotenv #, dotenv_values, find_dotenv
import os

load_dotenv()

def get_required_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise RuntimeError(
            f"Переменная окружения {key} не задана. "
            f"Проверь .env файл или переменные окружения контейнера."
        )
    return value

def get_bool_env(key: str, default: bool = False) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes")