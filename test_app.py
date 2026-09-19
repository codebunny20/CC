import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

import main
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

    def test_home_page_uses_separate_static_assets(self):
        client = app.test_client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'/static/css/style.css', response.data)
        self.assertIn(b'/static/js/app.js', response.data)

    def test_valid_conversion_requires_same_category(self):
        self.assertTrue(is_valid_conversion("Energy", "Calorie", "Joule"))
        self.assertFalse(is_valid_conversion("Energy", "Calorie", "Meter"))
        self.assertFalse(is_valid_conversion("Length", "Meter", "Kilogram"))

    def test_force_category_supports_requested_units(self):
        self.assertTrue(is_valid_conversion("Force", "Newton", "Kilonewton"))
        self.assertTrue(is_valid_conversion("Force", "Kilogram-force", "Gram-force"))
        self.assertTrue(is_valid_conversion("Force", "Kilogram-force", "Kilopond"))
        self.assertFalse(is_valid_conversion("Force", "Newton", "Meter"))

    def test_calculation_helper_matches_expected_math(self):
        self.assertEqual(main.evaluate_calculation(10, 2, "add"), 12)
        self.assertEqual(main.evaluate_calculation(10, 2, "subtract"), 8)
        self.assertEqual(main.evaluate_calculation(10, 2, "multiply"), 20)
        self.assertEqual(main.evaluate_calculation(10, 2, "divide"), 5)

    def test_calculation_helper_rejects_blank_or_invalid_input(self):
        with self.assertRaises(ValueError):
            main.evaluate_calculation("", 2, "add")
        with self.assertRaises(ValueError):
            main.evaluate_calculation(10, "abc", "multiply")
        with self.assertRaises(ZeroDivisionError):
            main.evaluate_calculation(10, 0, "divide")

    def test_coupon_helper_applies_realistic_discount_limits(self):
        self.assertEqual(main.calculate_coupon_result(100, 10, "percent"), (90.0, 10.0))
        self.assertEqual(main.calculate_coupon_result(100, 150, "percent"), (0.0, 100.0))
        self.assertEqual(main.calculate_coupon_result(100, 150, "amount"), (0.0, 100.0))
        self.assertEqual(main.calculate_coupon_result(100, 0, "percent"), (100.0, 0.0))

        with self.assertRaises(ValueError):
            main.calculate_coupon_result(-5, 10, "percent")
        with self.assertRaises(ValueError):
            main.calculate_coupon_result(100, -5, "percent")
        with self.assertRaises(ValueError):
            main.calculate_coupon_result(100, 10, "unknown")

    def test_conversion_helper_matches_reference_values(self):
        self.assertAlmostEqual(main.convert_value(1, "Length", "Meter", "Foot"), 3.280839895013123)
        self.assertAlmostEqual(main.convert_value(1, "Time", "Hour", "Minute"), 60)
        self.assertAlmostEqual(main.convert_value(100, "Temperature", "Celsius", "Fahrenheit"), 212)
        self.assertAlmostEqual(main.convert_value(32, "Temperature", "Fahrenheit", "Celsius"), 0)
        self.assertAlmostEqual(main.convert_value(1, "Energy", "Kilocalorie", "Joule"), 4184)
        self.assertAlmostEqual(main.convert_value(1, "Pressure", "Atmosphere", "Pascal"), 101325)

    def test_delete_history_clears_entries(self):
        with TemporaryDirectory() as temp_dir:
            temp_history_path = f"{temp_dir}/history.json"
            with patch.object(main, "HISTORY_PATH", temp_history_path):
                client = app.test_client()
                add_response = client.post(
                    "/history",
                    json={"value": "1 Meter to Foot", "result": "3.2808399 Foot", "timestamp": "Now"},
                )
                self.assertEqual(add_response.status_code, 200)

                delete_response = client.delete("/history")
                self.assertEqual(delete_response.status_code, 200)
                self.assertEqual(delete_response.get_json(), {"ok": True, "items": []})

                history_response = client.get("/history")
                self.assertEqual(history_response.status_code, 200)
                self.assertEqual(history_response.get_json(), {"items": []})


if __name__ == "__main__":
    unittest.main()
