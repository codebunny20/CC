import unittest

from main import app, is_valid_conversion


class AppTests(unittest.TestCase):
    def test_home_page_renders_html(self):
        client = app.test_client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Calculator + Converter", response.data)
        self.assertIn(b"Calculator", response.data)
        self.assertIn(b"Converter", response.data)
        self.assertIn(b"Light", response.data)
        self.assertIn(b"Dark", response.data)
        self.assertIn(b"System", response.data)
        self.assertIn(b"History", response.data)
        self.assertIn(b"Help", response.data)
        self.assertIn(b"Astronomical unit", response.data)
        self.assertIn(b"Decibel", response.data)
        self.assertIn(b"Pound-force", response.data)
        self.assertIn(b"Meganewton", response.data)

    def test_valid_conversion_requires_same_category(self):
        self.assertTrue(is_valid_conversion("Energy", "Calorie", "Joule"))
        self.assertFalse(is_valid_conversion("Energy", "Calorie", "Meter"))
        self.assertFalse(is_valid_conversion("Length", "Meter", "Kilogram"))

    def test_force_category_supports_requested_units(self):
        self.assertTrue(is_valid_conversion("Force", "Newton", "Kilonewton"))
        self.assertTrue(is_valid_conversion("Force", "Kilogram-force", "Gram-force"))
        self.assertTrue(is_valid_conversion("Force", "Kilogram-force", "Kilopond"))
        self.assertFalse(is_valid_conversion("Force", "Newton", "Meter"))


if __name__ == "__main__":
    unittest.main()
