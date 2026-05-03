class AppException(Exception):
 #  Base exception  #
    def __init__(self, message: str = "Application error"):
        self.message = message
        super().__init__(self.message)


class ExternalApiException(AppException):
    pass


class DatabaseException(AppException):
    pass


class MarketDataNotFoundException(AppException):
    pass

class DataNotFoundException(AppException):
    pass