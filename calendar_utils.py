from datetime import date, datetime


def parse_event_date(text):
    """Проверяет дату и возвращает её в формате date."""
    return datetime.strptime(text.strip(), "%d.%m.%Y").date()


def event_status(event_date, today=None):
    """Возвращает число дней до события или после него."""
    if today is None:
        today = date.today()

    difference = (event_date - today).days
    if difference > 0:
        return "Осталось дней: " + str(difference)
    if difference < 0:
        return "Прошло дней: " + str(-difference)
    return "Сегодня"
