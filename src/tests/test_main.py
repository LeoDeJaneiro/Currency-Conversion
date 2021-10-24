from datetime import date

from main import get_date_stack


def test_get_date_stack():
    date_stack = get_date_stack()
    today = date.today()
    start_day = date(today.year, 1, 1)
    delta = today - start_day
    assert isinstance(date_stack, list)
    assert len(date_stack) == delta.days + 1
    assert date_stack[0] == today.strftime("%Y-%m-%d")
    assert date_stack[len(date_stack) - 1] == start_day.strftime("%Y-%m-%d")
    assert today == start_day or date_stack[0] != date_stack[len(date_stack) - 1]
