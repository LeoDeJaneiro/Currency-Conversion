from typing import Tuple, Callable
import concurrent.futures
import logging
from sqlalchemy.orm import scoped_session

from model import Exchange_rate, Target_currency, Base_currency
from load import load_symbols, load_rates_of_date, SUPPORTED_BASE_SYMBOLS


def commit_currency_relations(session: scoped_session,
                              timeout: int) -> Tuple[dict, dict]:
    try:
        symbols = load_symbols(timeout)
        target_currencies: dict = {}
        base_currencies: dict = {}
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


def execute_load(**kwargs: dict) -> Callable:
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


def load_data_multi_processes(**kwargs: dict) -> None:
    Session = kwargs.get("Session")
    max_workers = kwargs.get("max_workers")
    dates = kwargs.get("dates")

    with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers) as executor:
        future_to_load: dict = {}
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
                logging.info(f'{current_date} success')
                future.result()
            except Exception as e:
                logging.error(f'{current_date} {repr(e)}')
