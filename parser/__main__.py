from parser.domain import EBook
from parser.orchestrator import run

def main(books: EBook|list[EBook], headless = True, persistent_context = True):
    run(books=books, headless = headless, persistent_context = persistent_context)

if __name__  == '__main__':
    pass
