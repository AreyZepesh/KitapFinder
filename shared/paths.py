from pathlib import Path
from shutil import rmtree
import os

env_base_dir = os.getenv( "KITAPFINDER_BASE_DIR")
local_base_dir = Path(__file__).parent.parent.absolute()
BASE_DIR = Path( env_base_dir if env_base_dir else local_base_dir ) 
LOGS_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "output"
TMP_DIR = BASE_DIR / "tmp"
PROFILE_DIR = BASE_DIR / "parser" / "profile"

def create_dirs():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

def rm_log_files():
    files = ["_urls.txt", "_error.txt"]
    for file in files:
        file_path = Path(LOGS_DIR / file)
        if file_path.exists():
            os.remove(file_path)

    dirs = [
        "err", 
        # "_nores", 
        # "wb", 
        "zero_page"]
    for dir in dirs:
        dir_path = Path(LOGS_DIR / dir)
        if os.path.exists(dir_path):
            rmtree(dir_path)

# def rm_tmp_files():
    # ...
