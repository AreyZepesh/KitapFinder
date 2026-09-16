class ParserControlException(Exception):
    """База для исключений-сигналов, которые должны пробивать все уровни
    try_and_log_decor без ретраев и без логирования как обычная ошибка."""

class AntibotDetectedError(ParserControlException):
    """Антибот заблокировал/повредил текущую страницу или контекст."""