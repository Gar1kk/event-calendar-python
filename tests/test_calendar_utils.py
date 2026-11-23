import unittest
from datetime import date

from calendar_utils import parse_event_date, event_status


class CalendarUtilsTests(unittest.TestCase):
    def test_correct_date(self):
        self.assertEqual(parse_event_date("25.12.2026"), date(2026, 12, 25))

    def test_wrong_date(self):
        with self.assertRaises(ValueError):
            parse_event_date("31.02.2026")

    def test_wrong_format(self):
        with self.assertRaises(ValueError):
            parse_event_date("2026-12-25")

    def test_future_event(self):
        self.assertEqual(
            event_status(date(2026, 12, 25), date(2026, 12, 23)),
            "Осталось дней: 2"
        )

    def test_past_event(self):
        self.assertEqual(
            event_status(date(2026, 12, 21), date(2026, 12, 23)),
            "Прошло дней: 2"
        )

    def test_today_event(self):
        self.assertEqual(
            event_status(date(2026, 12, 23), date(2026, 12, 23)),
            "Сегодня"
        )


if __name__ == "__main__":
    unittest.main()
