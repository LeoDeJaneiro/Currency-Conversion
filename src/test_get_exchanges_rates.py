import datetime

from get_exchange_rates import date_string_from_delta, DATE_STRINGS, DATES_TO_RETRIEVE


def test_date_string_from_delta():
    delta = 2
    date_string = date_string_from_delta(delta)
    expectation = datetime.datetime.now() - datetime.timedelta(days=delta)
    assert date_string == expectation.strftime("%Y-%m-%d")


def test_DATE_STRINGS():
    assert len(DATE_STRINGS) == DATES_TO_RETRIEVE
    assert DATE_STRINGS[0] == date_string_from_delta(0)
    assert DATE_STRINGS[len(DATE_STRINGS) -
                        1] == date_string_from_delta(DATES_TO_RETRIEVE - 1)
