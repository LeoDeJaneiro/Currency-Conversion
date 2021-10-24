import json
import urllib.request
from decouple import config

SUPPORTED_BASE_SYMBOLS = ["EUR", "USD"]
BASE_URL = 'http://api.exchangeratesapi.io/v1'
API_ACCESS_KEY = config('API_ACCESS_KEY')


def get_url(**kwargs: dict) -> str:
    endpoint = kwargs.get("endpoint")
    date_string = kwargs.get("date_string")
    if endpoint == "rates":
        return f'{BASE_URL}/{date_string}?access_key={API_ACCESS_KEY}'
    if endpoint == "symbols":
        return f'{BASE_URL}/symbols?access_key={API_ACCESS_KEY}'


def load_url(url: str, timeout: int) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        response_string = conn.read().decode('utf-8')
        return json.loads(response_string)


def load_rates_of_date(date: str, timeout: int) -> dict:
    """ Loads all EUR-base rates per date.
        Derives rates for all bases in BASE_TO_BE_DERIVED.
        Returns dict with base_currency as key and target_currency: rate dicts as value"""

    url = get_url(endpoint="rates", date_string=date)
    rate_response = load_url(url, timeout)
    rates_for_EUR = rate_response.get("rates", {})
    rates_of_date = {"EUR": rates_for_EUR}
    for base_symbol in (symbol for symbol in SUPPORTED_BASE_SYMBOLS
                        if symbol != 'EUR'):
        rates_of_date = {
            **rates_of_date, base_symbol: {
                target_symbol: rate * rates_for_EUR.get(base_symbol)
                for target_symbol, rate in rate_response.get("rates",
                                                             {}).items()
            }
        }
    return rates_of_date


def load_symbols(timeout: int) -> dict:
    url = get_url(endpoint="symbols")
    return load_url(url, timeout).get("symbols")
