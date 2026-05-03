import requests
from app.config import settings


class ExternalApiError(Exception):
    pass


class ExternalApiClient:
    def fetch_market_data(self, symbol: str):
        try:
            params = {
                "symbol": symbol,
                "apikey": settings.API_KEY
            }

            response = requests.get(
                settings.EXTERNAL_API_URL,
                params=params,
                timeout=settings.API_TIMEOUT
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise ExternalApiError("External API request timed out")

        except requests.exceptions.ConnectionError:
            raise ExternalApiError("Could not connect to external API")

        except requests.exceptions.HTTPError:
            raise ExternalApiError("External API returned an error")

        except ValueError:
            raise ExternalApiError("Invalid JSON response from external API")
