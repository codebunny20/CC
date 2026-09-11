import unittest

from main import app


class AppTests(unittest.TestCase):
    def test_home_page_renders_html(self):
        client = app.test_client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Calculator + Converter", response.data)
        self.assertIn(b"Calculator", response.data)
        self.assertIn(b"Converter", response.data)
        self.assertIn(b"Astronomical unit", response.data)
        self.assertIn(b"Decibel", response.data)


if __name__ == "__main__":
    unittest.main()
