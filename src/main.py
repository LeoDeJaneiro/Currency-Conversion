from datetime import date, timedelta
import logging
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from model import create_schema
from commit import commit_currency_relations, load_data_threaded

logging.basicConfig(filename='get_exchange_rates.log',
                    format='%(asctime)s %(levelname)s:%(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p',
                    level=logging.DEBUG)

SUPPORTED_BASE_SYMBOLS = ["EUR", "USD"]
BASE_URL = 'http://api.exchangeratesapi.io/v1'
API_ACCESS_KEY = config('API_ACCESS_KEY')


def get_date_stack() -> list[str]:
    today = date.today()
    year_delta = today - date(today.year, 1, 1)

    def date_string_from_delta(delta: int):
        new_date = today - timedelta(days=delta)
        return new_date.strftime("%Y-%m-%d")

    return [
        date_string_from_delta(delta) for delta in range(year_delta.days + 1)
    ]


def main(timeout: int) -> None:
    USER = config('POSTGRESQL_USER')
    PASSWORD = config('POSTGRES_PASSWORD')
    DB = config('POSTGRES_DB')
    MAX_WORKERS = 25

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
                       max_workers=MAX_WORKERS,
                       timeout=timeout)


main(2000)
