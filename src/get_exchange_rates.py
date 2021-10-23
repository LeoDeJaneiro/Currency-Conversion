import json
from datetime import date, timedelta
import concurrent.futures
import urllib.request
import logging
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from model import create_schema, Exchange_rate, Target_currency, Base_currency

logging.basicConfig(filename='get_exchange_rates.log',
                    format='%(asctime)s %(levelname)s:%(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p',
                    level=logging.DEBUG)

SUPPORTED_BASE_SYMBOLS = ["EUR", "USD"]
BASE_URL = 'http://api.exchangeratesapi.io/v1'
API_ACCESS_KEY = config('API_ACCESS_KEY')


def get_date_stack():
    today = date.today()
    year_delta = today - date(today.year, 1, 1)

    def date_string_from_delta(delta: int):
        new_date = today - timedelta(days=delta)
        return new_date.strftime("%Y-%m-%d")

    return [
        date_string_from_delta(delta) for delta in range(year_delta.days + 1)
    ]


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


def load_symbols(timeout):
    url = get_url(endpoint="symbols")
    return load_url(url, timeout).get("symbols")


def execute_load(**kwargs):
    session = kwargs.get("session")
    date = kwargs.get("date")
    timeout = kwargs.get("timeout")
    base_currencies = kwargs.get("base_currencies")
    target_currencies = kwargs.get("target_currencies")

    def load():
        try:
            logging.info(f'execute_load() {date} started')
            date_rates: dict = load_rates_of_date(date, timeout)
            for base_currency, rates in date_rates.items():
                for target_currency, rate in rates.items():
                    exchange_rate = Exchange_rate(
                        base_currency_id=base_currencies.get(base_currency).id,
                        target_currency_id=target_currencies.get(
                            target_currency).id,
                        date=date,
                        rate=rate)
                    session.add(exchange_rate)
            session.commit()
        except Exception as e:
            logging.error(f'load() for {date}: {e}')

    return load()


def load_data_threaded(**kwargs):
    Session = kwargs.get("Session")
    max_workers = kwargs.get("max_workers")
    dates = kwargs.get("dates")

    with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers) as executor:
        future_to_load = {}
        for date in dates:
            session = Session()
            future_to_load = {
                **future_to_load,
                executor.submit(
                    execute_load(**kwargs, date=date, session=session)):
                date
            }

        for future in concurrent.futures.as_completed(future_to_load):
            current_date = future_to_load[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f'{current_date} {repr(e)}')
            else:
                logging.info(f'{current_date} success')


def commit_currency_relations(session, timeout):
    try:
        symbols = load_symbols(timeout)
        target_currencies = {}
        base_currencies = {}
        for symbol, name in symbols.items():
            target_currency = Target_currency(symbol=symbol, name=name)
            target_currencies = {**target_currencies, symbol: target_currency}
            session.add(target_currency)
            if symbol in SUPPORTED_BASE_SYMBOLS:
                base_currency = Base_currency(symbol=symbol, name=name)
                base_currencies = {**base_currencies, symbol: base_currency}
                session.add(base_currency)
        session.commit()
        return (base_currencies, target_currencies)
    except Exception as e:
        logging.error(f'commit_currency_relations() {repr(e)}')


def orchestrate_data_load(timeout):
    USER = config('POSTGRESQL_USER')
    PASSWORD = config('POSTGRES_PASSWORD')
    DB = config('POSTGRES_DB')

    engine = create_engine(
        f'postgresql://{USER}:{PASSWORD}@localhost/{DB}',
        # limits engine instantiation of 1 connection per thread
        pool_size=1,
        max_overflow=0)

    create_schema(engine)

    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    base_currencies, target_currencies = commit_currency_relations(
        session, timeout)
    dates = get_date_stack()
    load_data_threaded(dates=dates,
                       Session=Session,
                       base_currencies=base_currencies,
                       target_currencies=target_currencies,
                       max_workers=25,
                       timeout=timeout)


orchestrate_data_load(2000)
