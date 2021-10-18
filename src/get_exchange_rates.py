import os
from datetime import date, timedelta
import concurrent.futures
import urllib.request
import logging
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .model import Rate, Base_currency

logging.basicConfig(filename='get_exchange_rates.log',
                    format='%(asctime)s %(levelname)s:%(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    encoding='utf-8',
                    level=logging.DEBUG)

BASE_URL = 'http://api.exchangeratesapi.io/v1'
DATES_TO_RETRIEVE = 250

API_ACCESS_KEY = ''
# API_ACCESS_KEY = config('API_ACCESS_KEY')
# POSTGRESQL_USER = config('POSTGRESQL_USER')
# POSTGRESQL_PW = config('POSTGRESQL_PW')


def date_string_from_delta(delta: int):
    today = date.today()
    def get_date_string():
        date = today - timedelta(days=delta)
        return date.strftime("%Y-%m-%d")

    return get_date_string()


DATE_STRINGS = [
    date_string_from_delta(delta) for delta in range(DATES_TO_RETRIEVE)
]

urls = {
    "date": lambda date_string: f'{BASE_URL}/{date_string}?access_key={API_ACCESS_KEY}',
    "symbols": lambda _: f'{BASE_URL}/symbols?access_key={API_ACCESS_KEY}'
}


def load_url(url: str, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.read().decode('utf-8')


def load_date(date: str, timeout):
    url = urls.get('date')(date)
    return load_url(url, timeout)


def load_symbols(timeout):
    url = urls.get('symbols')()
    return load_url(url, timeout)


def execute_load(session, date, timeout):
    def load():
        logging.info(f'{date} started')
        response = load_date(date, timeout)

        # session

    return load()


def load_data_threaded(Session, timeout, max_workers):
    # high-level interface for asynchronously executing callables
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers) as executor:
        future_to_load = {}
        for date in DATE_STRINGS:
            session = Session()
            future_to_load = {
                **future_to_load,
                executor.submit(execute_load(session, date, timeout), date, 60):
                date
            }
        # future_to_load = {executor.submit(execute_load(session, date, timeout), date, 60): date for date in DATE_STRINGS}
        for future in concurrent.futures.as_completed(future_to_load):
            current_date = future_to_load[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f'{current_date} {repr(e)}')
            else:
                logging.info(f'{current_date} success')


def orchestrate_data_load(timeout):
    # allows instantiation of 1 connection per thread
    engine = create_engine('postgresql://me@localhost/mydb',
                           pool_size=1,
                           max_overflow=0)
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    # instantiate SQLAlchemy classes

    # get currency's symbols
    symbols = load_symbols(timeout)

    # if not exist add currency as column to table rate

    # start data load
    load_data_threaded(Session, timeout, 25)
