import json
import math
import os

from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder="templates", static_folder="static")

HISTORY_PATH = os.path.join(os.path.dirname(__file__), "history.json")

UNIT_CATEGORIES = {
    "Length": {
        "type": "linear",
        "base": "Meter",
        "units": {
            "Meter": 1,
            "Kilometer": 1000,
            "Centimeter": 0.01,
            "Millimeter": 0.001,
            "Micrometer": 1e-6,
            "Nanometer": 1e-9,
            "Inch": 0.0254,
            "Foot": 0.3048,
            "Yard": 0.9144,
            "Mile": 1609.344,
            "Nautical mile": 1852,
            "Light-year": 9.4607304725808e15,
            "Astronomical unit": 149597870700,
            "Parsec": 3.085677581491367e16,
        },
    },
    "Mass": {
        "type": "linear",
        "base": "Kilogram",
        "units": {
            "Kilogram": 1,
            "Gram": 0.001,
            "Milligram": 1e-6,
            "Microgram": 1e-9,
            "Tonne": 1000,
            "Pound": 0.45359237,
            "Ounce": 0.028349523125,
            "Stone": 6.35029318,
            "Carat": 0.0002,
            "Atomic mass unit": 1.66053906660e-27,
        },
    },
    "Temperature": {
        "type": "temperature",
        "units": ["Kelvin", "Celsius", "Fahrenheit", "Rankine"],
    },
    "Time": {
        "type": "linear",
        "base": "Second",
        "units": {
            "Second": 1,
            "Minute": 60,
            "Hour": 3600,
            "Day": 86400,
            "Week": 604800,
            "Month": 2629746,
            "Year": 31557600,
            "Century": 3155760000,
        },
    },
    "Volume": {
        "type": "linear",
        "base": "Cubic meter",
        "units": {
            "Cubic meter": 1,
            "Liter": 0.001,
            "Milliliter": 1e-6,
            "Cubic centimeter": 1e-6,
            "Gallon": 0.003785411784,
            "Quart": 0.000946352946,
            "Pint": 0.000473176473,
            "Cup": 0.0002365882365,
            "Fluid ounce": 2.95735295625e-5,
        },
    },
    "Energy": {
        "type": "linear",
        "base": "Joule",
        "units": {
            "Joule": 1,
            "Calorie": 4.184,
            "Kilocalorie": 4184,
            "Electronvolt": 1.602176634e-19,
            "British thermal unit": 1055.05585262,
            "Kilowatt-hour": 3600000,
        },
    },
    "Pressure": {
        "type": "linear",
        "base": "Pascal",
        "units": {
            "Pascal": 1,
            "Bar": 100000,
            "Atmosphere": 101325,
        },
    },
    "Speed": {
        "type": "linear",
        "base": "Meter per second",
        "units": {
            "Meter per second": 1,
            "Kilometer per hour": 0.2777777777777778,
            "Mile per hour": 0.44704,
            "Foot per second": 0.3048,
            "Knot": 0.5144444444444445,
            "Centimeter per second": 0.01,
            "Mach": 340.294,
            "Light speed": 299792458,
        },
    },
    "Force": {
        "type": "linear",
        "base": "Newton",
        "units": {
            "Newton": 1,
            "Dyne": 1e-5,
            "Pound-force": 4.4482216152605,
            "Ounce-force": 0.27801385095378125,
            "Kilogram-force": 9.80665,
            "Kilopond": 9.80665,
            "Gram-force": 0.00980665,
            "Poundal": 0.138254954376,
            "Kip": 4448.2216152605,
            "Ton-force": 9806.65,
            "Millinewton": 0.001,
            "Kilonewton": 1000,
            "Meganewton": 1000000,
        },
    },
    "Electricity": {
        "type": "reference",
        "units": ["Ampere", "Volt", "Ohm", "Watt", "Farad", "Henry", "Siemens", "Coulomb"],
    },
    "Illumination": {
        "type": "reference",
        "units": ["Lux"],
    },
    "Luminous intensity": {
        "type": "reference",
        "units": ["Candela"],
    },
    "Radiation": {
        "type": "reference",
        "units": ["Gray", "Sievert", "Becquerel"],
    },
    "Magnetism": {
        "type": "reference",
        "units": ["Tesla"],
    },
    "Sound level": {
        "type": "reference",
        "units": ["Decibel"],
    },
}

def _load_history():
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as history_file:
            payload = json.load(history_file)
            return payload if isinstance(payload, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def _save_history(entries):
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as history_file:
            json.dump(entries, history_file, indent=2)
    except OSError:
        pass


def _coerce_numeric(value):
    if value is None or isinstance(value, bool):
        raise ValueError("Value is required")

    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError("Value is required")
        try:
            number = float(stripped)
        except ValueError as exc:
            raise ValueError("Value must be numeric") from exc
    else:
        raise ValueError("Value must be numeric")

    if not math.isfinite(number):
        raise ValueError("Value must be finite")
    return number


def _convert_temperature(value, from_unit, to_unit):
    to_kelvin = {
        "Kelvin": lambda x: x,
        "Celsius": lambda x: x + 273.15,
        "Fahrenheit": lambda x: ((x + 459.67) * 5) / 9,
        "Rankine": lambda x: (x * 5) / 9,
    }
    from_kelvin = {
        "Kelvin": lambda x: x,
        "Celsius": lambda x: x - 273.15,
        "Fahrenheit": lambda x: (x * 9) / 5 - 459.67,
        "Rankine": lambda x: (x * 9) / 5,
    }
    return from_kelvin[to_unit](to_kelvin[from_unit](value))


def evaluate_calculation(value1, value2, operation):
    left = _coerce_numeric(value1)
    right = _coerce_numeric(value2)
    op = (operation or "").strip().lower()

    if op == "add":
        return left + right
    if op == "subtract":
        return left - right
    if op == "multiply":
        return left * right
    if op == "divide":
        if right == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return left / right

    raise ValueError(f"Unsupported operation: {operation}")


def calculate_coupon_result(price, discount_value, discount_type):
    price_value = _coerce_numeric(price)
    discount_value_value = _coerce_numeric(discount_value)

    if price_value < 0:
        raise ValueError("Price must be non-negative")
    if discount_value_value < 0:
        raise ValueError("Discount must be non-negative")

    normalized_type = (discount_type or "").strip().lower()
    if normalized_type == "percent":
        capped_percentage = min(max(discount_value_value, 0), 100)
        savings = min(price_value * capped_percentage / 100, price_value)
    elif normalized_type == "amount":
        savings = min(discount_value_value, price_value)
    else:
        raise ValueError(f"Unsupported discount type: {discount_type}")

    final_price = max(price_value - savings, 0)
    return final_price, savings


def convert_value(value, category, from_unit, to_unit):
    numeric_value = _coerce_numeric(value)
    config = UNIT_CATEGORIES.get(category)
    if not config:
        raise ValueError(f"Unknown category: {category}")
    if not from_unit or not to_unit:
        raise ValueError("Both units are required")

    if config["type"] == "temperature":
        if from_unit not in config["units"] or to_unit not in config["units"]:
            raise ValueError("Temperature conversion requires valid units from the same category")
        return _convert_temperature(numeric_value, from_unit, to_unit)

    if config["type"] == "linear":
        if from_unit not in config["units"] or to_unit not in config["units"]:
            raise ValueError("Linear conversion requires valid units from the same category")
        return numeric_value * config["units"][from_unit] / config["units"][to_unit]

    if config["type"] == "reference":
        if from_unit != to_unit or from_unit not in config["units"]:
            raise ValueError("Reference units must match exactly")
        return numeric_value

    raise ValueError(f"Unsupported category type: {config['type']}")


def is_valid_conversion(category, from_unit, to_unit):
    if not category or not from_unit or not to_unit:
        return False

    config = UNIT_CATEGORIES.get(category)
    if not config:
        return False

    if config["type"] == "temperature":
        return from_unit in config["units"] and to_unit in config["units"]

    if config["type"] == "linear":
        return from_unit in config["units"] and to_unit in config["units"]

    if config["type"] == "reference":
        return from_unit == to_unit and from_unit in config["units"]

    return False


@app.route("/")
def home():
    return render_template("index.html", category_config=UNIT_CATEGORIES)


@app.route("/history")
def history_api():
    entries = _load_history()
    return jsonify({"items": entries[-8:]})


@app.route("/history", methods=["POST"])
def add_history_entry():
    data = request.get_json(silent=True) or {}
    value = data.get("value")
    result = data.get("result")
    timestamp = data.get("timestamp") or "Just now"

    if not isinstance(value, str) or not value.strip():
        return jsonify({"ok": False, "error": "Missing value"}), 400

    entries = _load_history()
    entries.append({
        "value": value.strip(),
        "result": result if isinstance(result, str) else "",
        "timestamp": timestamp,
    })
    _save_history(entries[-20:])
    return jsonify({"ok": True, "items": entries[-20:]})


@app.route("/history", methods=["DELETE"])
def delete_history():
    _save_history([])
    return jsonify({"ok": True, "items": []})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

