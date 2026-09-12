import json
import os

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

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
            "Knot": 0.5144444444444445,
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


PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CC Unit Converter</title>
    <style>
        :root {
            color-scheme: light;
            --bg: #edf2f7;
            --bg-spot-1: rgba(31, 122, 140, 0.22);
            --bg-spot-2: rgba(11, 79, 108, 0.18);
            --panel: #ffffff;
            --panel-strong: #f7fbfe;
            --ink: #102a43;
            --muted: #627d98;
            --accent: #1f7a8c;
            --accent-strong: #0b4f6c;
            --border: #d9e2ec;
            --shadow: 0 18px 45px rgba(16, 42, 67, 0.12);
            --control-bg: #edf2f7;
            --result-bg: #f8fcfd;
            --result-border: #d6eef3;
        }

        body[data-theme="dark"] {
            color-scheme: dark;
            --bg: #08121f;
            --bg-spot-1: rgba(35, 139, 164, 0.28);
            --bg-spot-2: rgba(9, 90, 126, 0.26);
            --panel: #0f1b2d;
            --panel-strong: #13233a;
            --ink: #e5eef8;
            --muted: #9fb4ca;
            --accent: #43b4c8;
            --accent-strong: #2a8ca3;
            --border: #2a3951;
            --shadow: 0 20px 55px rgba(0, 0, 0, 0.38);
            --control-bg: #13233a;
            --result-bg: #102033;
            --result-border: #22354f;
        }

        @media (prefers-color-scheme: dark) {
            body[data-theme="system"] {
                color-scheme: dark;
                --bg: #08121f;
                --bg-spot-1: rgba(35, 139, 164, 0.28);
                --bg-spot-2: rgba(9, 90, 126, 0.26);
                --panel: #0f1b2d;
                --panel-strong: #13233a;
                --ink: #e5eef8;
                --muted: #9fb4ca;
                --accent: #43b4c8;
                --accent-strong: #2a8ca3;
                --border: #2a3951;
                --shadow: 0 20px 55px rgba(0, 0, 0, 0.38);
                --control-bg: #13233a;
                --result-bg: #102033;
                --result-border: #22354f;
            }
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, Helvetica, sans-serif;
            color: var(--ink);
            background:
                radial-gradient(circle at top left, var(--bg-spot-1), transparent 34%),
                radial-gradient(circle at bottom right, var(--bg-spot-2), transparent 28%),
                var(--bg);
            overflow-y: auto;
            padding: 24px;
        }

        .shell {
            width: min(100%, 1040px);
            display: grid;
            gap: 20px;
            margin: 0 auto;
        }

        .topbar {
            display: grid;
            grid-template-columns: 1.2fr auto;
            gap: 20px;
            align-items: center;
        }

        .card {
            background: var(--panel);
            border: 1px solid rgba(217, 226, 236, 0.9);
            border-radius: 24px;
            box-shadow: var(--shadow);
            overflow: visible;
        }

        .hero {
            padding: 32px;
            background: linear-gradient(145deg, var(--panel) 0%, var(--panel-strong) 100%);
        }

        .mode-switch {
            display: inline-flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }

        .header-actions {
            display: grid;
            justify-items: end;
            gap: 12px;
        }

        .mode-button {
            width: auto;
            min-width: 132px;
            padding: 12px 16px;
            background: var(--control-bg);
            color: var(--ink);
            box-shadow: none;
            border: 1px solid var(--border);
        }

        .settings-button,
        .history-button {
            min-width: 110px;
            padding: 12px 16px;
            background: var(--control-bg);
            color: var(--ink);
            box-shadow: none;
            border: 1px solid var(--border);
        }

        .settings-window,
        .dialog-window {
            position: fixed;
            top: 92px;
            right: 24px;
            width: min(320px, calc(100vw - 32px));
            display: none;
            z-index: 100;
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 18px;
            box-shadow: var(--shadow);
            padding: 18px;
        }

        .settings-window.open,
        .dialog-window.open {
            display: grid;
            gap: 12px;
        }

        .settings-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 4px;
        }

        .settings-header h3 {
            margin: 0;
            font-size: 1.05rem;
        }

        .settings-close {
            min-width: 0;
            width: auto;
            padding: 8px 10px;
            background: var(--control-bg);
            color: var(--ink);
            border: 1px solid var(--border);
            border-radius: 10px;
            box-shadow: none;
        }

        .settings-section {
            display: grid;
            gap: 8px;
        }

        .settings-label {
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--muted);
        }

        .settings-options,
        .settings-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .settings-option,
        .settings-action {
            flex: 1 1 0;
            min-width: 84px;
            padding: 10px 12px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: var(--control-bg);
            color: var(--ink);
            box-shadow: none;
        }

        .dialog-body {
            display: grid;
            gap: 10px;
            color: var(--ink);
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .dialog-body p {
            margin: 0;
            color: var(--muted);
        }

        .history-list {
            display: grid;
            gap: 8px;
            margin: 0;
            padding: 0;
            list-style: none;
        }

        .history-item {
            padding: 10px 12px;
            border-radius: 12px;
            background: var(--result-bg);
            border: 1px solid var(--result-border);
        }

        .history-item strong {
            display: block;
            margin-bottom: 3px;
        }

        .settings-option.active {
            background: linear-gradient(135deg, var(--accent), var(--accent-strong));
            border-color: transparent;
            color: #fff;
        }

        .mode-button.active {
            background: linear-gradient(135deg, var(--accent), var(--accent-strong));
            color: #fff;
            border-color: transparent;
            box-shadow: 0 10px 22px rgba(31, 122, 140, 0.22);
        }

        .eyebrow {
            margin: 0 0 10px;
            color: var(--accent);
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        h1 {
            margin: 0;
            font-size: clamp(2rem, 3vw, 3.15rem);
            line-height: 1.05;
        }

        .lede {
            margin: 16px 0 0;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.6;
            max-width: 56ch;
        }

        .converter {
            padding: 32px;
            display: grid;
            gap: 16px;
        }

        .calculator {
            padding: 32px;
            display: grid;
            gap: 16px;
        }

        .panel {
            display: none;
        }

        .shell[data-mode="calculator"] .calculator,
        .shell[data-mode="converter"] .converter {
            display: grid;
        }

        .field {
            display: grid;
            gap: 8px;
        }

        .dropdown {
            position: relative;
        }

        .dropdown-toggle {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            border-radius: 14px;
            border: 1px solid var(--border);
            font: inherit;
            padding: 14px 15px;
            background: var(--panel);
            color: var(--ink);
            cursor: pointer;
            box-shadow: none;
        }

        .dropdown-toggle:focus,
        .dropdown-option:focus {
            outline: 3px solid rgba(31, 122, 140, 0.18);
            border-color: var(--accent);
        }

        .dropdown-menu {
            position: absolute;
            top: calc(100% + 8px);
            left: 0;
            right: 0;
            z-index: 30;
            display: none;
            max-height: min(260px, 40vh);
            overflow-y: auto;
            overscroll-behavior: contain;
            scrollbar-gutter: stable;
            padding: 8px;
            border-radius: 14px;
            border: 1px solid var(--border);
            background: var(--panel);
            box-shadow: var(--shadow);
        }

        .dropdown.open .dropdown-menu {
            display: grid;
            gap: 6px;
        }

        .dropdown-option {
            width: 100%;
            text-align: left;
            border: none;
            border-radius: 10px;
            padding: 10px 12px;
            background: transparent;
            color: var(--ink);
            box-shadow: none;
            cursor: pointer;
        }

        .dropdown-option.selected,
        .dropdown-option:hover {
            background: rgba(31, 122, 140, 0.1);
        }

        .chevron {
            font-size: 0.8rem;
            color: var(--muted);
            transition: transform 160ms ease;
        }

        .dropdown.open .chevron {
            transform: rotate(180deg);
        }

        label {
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--ink);
        }

        input, select, button {
            width: 100%;
            border-radius: 14px;
            border: 1px solid var(--border);
            font: inherit;
            padding: 14px 15px;
            background: var(--panel);
            color: var(--ink);
        }

        input:focus, select:focus, button:focus {
            outline: 3px solid rgba(31, 122, 140, 0.18);
            border-color: var(--accent);
        }

        .select-hidden {
            display: none;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
        }

        button {
            border: none;
            background: linear-gradient(135deg, var(--accent), var(--accent-strong));
            color: white;
            font-weight: 700;
            cursor: pointer;
            transition: transform 120ms ease, box-shadow 120ms ease;
            box-shadow: 0 10px 22px rgba(31, 122, 140, 0.22);
        }

        button:hover {
            transform: translateY(-1px);
        }

        .result {
            padding: 16px;
            border-radius: 16px;
            background: var(--result-bg);
            border: 1px solid var(--result-border);
            min-height: 76px;
            display: grid;
            align-content: center;
            gap: 4px;
        }

        .result strong {
            font-size: 1.35rem;
        }

        .result p {
            margin: 0;
            color: var(--muted);
            line-height: 1.5;
        }

        .side {
            padding: 24px;
            display: grid;
            gap: 16px;
            align-content: start;
        }

        .side h2 {
            margin: 0;
            font-size: 1.1rem;
        }

        .unit-list {
            margin: 0;
            padding-left: 18px;
            color: var(--muted);
            line-height: 1.75;
        }

        .operation-grid {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 12px;
            align-items: center;
        }

        .operator {
            min-width: 72px;
            padding-left: 10px;
            padding-right: 10px;
            text-align: center;
            background: var(--result-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            font-weight: 700;
            color: var(--accent-strong);
        }

        @media (max-width: 820px) {
            .shell {
                grid-template-columns: 1fr;
            }

            .topbar {
                grid-template-columns: 1fr;
            }

            .mode-switch {
                justify-content: stretch;
            }

            .theme-switch {
                justify-content: stretch;
            }

            .mode-button {
                min-width: 0;
                flex: 1 1 0;
            }

            .hero, .converter, .calculator, .side {
                padding: 24px;
            }

            .grid-2 {
                grid-template-columns: 1fr;
            }

            .operation-grid {
                grid-template-columns: 1fr;
            }

            .operator {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <main class="shell" id="appShell" data-mode="converter">
        <section class="card hero topbar">
            <div>
                <p class="eyebrow">CC Calculator + Converter</p>
                <h1>Switch instantly between calculations and unit conversion.</h1>
                <p class="lede">
                    Use calculator mode for quick math, or switch to converter mode for length, mass, temperature,
                    time, volume, energy, pressure, speed, and specialized measurement units.
                </p>
            </div>

            <div class="header-actions">
                <div class="mode-switch" role="tablist" aria-label="App mode">
                    <button class="mode-button active" id="calculatorModeButton" type="button">Calculator</button>
                    <button class="mode-button" id="converterModeButton" type="button">Converter</button>
                </div>

                <button class="mode-button history-button" id="historyButton" type="button" aria-label="History" aria-expanded="false">🕘 History</button>
                <button class="mode-button settings-button" id="settingsButton" type="button" aria-label="Settings" aria-expanded="false">⚙ Settings</button>
            </div>
        </section>

        <section class="card calculator panel" aria-label="Calculator panel">
            <div class="field">
                <label for="calculatorValue1">First value</label>
                <input id="calculatorValue1" type="number" inputmode="decimal" value="1" />
            </div>

            <div class="operation-grid">
                <div class="field">
                    <label for="calculatorValue2">Second value</label>
                    <input id="calculatorValue2" type="number" inputmode="decimal" value="1" />
                </div>

                <div class="operator" aria-hidden="true">=</div>

                <div class="field">
                    <label for="calculatorOperation">Operation</label>
                    <select id="calculatorOperation">
                        <option value="add">Add</option>
                        <option value="subtract">Subtract</option>
                        <option value="multiply">Multiply</option>
                        <option value="divide">Divide</option>
                    </select>
                </div>
            </div>

            <button id="calculateButton" type="button">Calculate</button>

            <div class="result" id="calculatorResult" aria-live="polite">
                <strong>Result will appear here</strong>
                <p>Enter values and choose an operation.</p>
            </div>
        </section>

        <section class="card converter panel" aria-label="Unit converter panel">
            <div class="field">
                <label for="category">Category</label>
                <div id="categoryDropdown" class="dropdown" aria-label="Category selector">
                    <button id="categoryToggle" class="dropdown-toggle" type="button" aria-expanded="false" aria-controls="categoryMenu">
                        <span id="categoryLabel">Select a category</span>
                        <span class="chevron" aria-hidden="true">▾</span>
                    </button>
                    <div id="categoryMenu" class="dropdown-menu" role="listbox" aria-label="Category options"></div>
                </div>
                <select id="category" class="select-hidden"></select>
            </div>

            <div class="field">
                <label for="value">Value</label>
                <input id="value" type="number" inputmode="decimal" value="1" />
            </div>

            <div class="grid-2">
                <div class="field">
                    <label for="fromUnit">From</label>
                    <div id="fromUnitDropdown" class="dropdown" aria-label="From unit selector">
                        <button id="fromUnitToggle" class="dropdown-toggle" type="button" aria-expanded="false" aria-controls="fromUnitMenu">
                            <span id="fromUnitLabel">Select a unit</span>
                            <span class="chevron" aria-hidden="true">▾</span>
                        </button>
                        <div id="fromUnitMenu" class="dropdown-menu" role="listbox" aria-label="From unit options"></div>
                    </div>
                    <select id="fromUnit" class="select-hidden"></select>
                </div>
                <div class="field">
                    <label for="toUnit">To</label>
                    <div id="toUnitDropdown" class="dropdown" aria-label="To unit selector">
                        <button id="toUnitToggle" class="dropdown-toggle" type="button" aria-expanded="false" aria-controls="toUnitMenu">
                            <span id="toUnitLabel">Select a unit</span>
                            <span class="chevron" aria-hidden="true">▾</span>
                        </button>
                        <div id="toUnitMenu" class="dropdown-menu" role="listbox" aria-label="To unit options"></div>
                    </div>
                    <select id="toUnit" class="select-hidden"></select>
                </div>
            </div>

            <button id="convertButton" type="button">Convert</button>

            <div class="result" id="result" aria-live="polite">
                <strong>Result will appear here</strong>
                <p>Select a category and unit pair to convert.</p>
            </div>
        </section>

        <section class="card side">
            <h2>Included units</h2>
            <p class="lede" style="margin: 0; font-size: 0.95rem;">
                The converter includes every unit i can think of at the moment. Where a unit is a reference quantity rather than a
                directly convertible scale, it is still available in the catalog.
            </p>
            <ul class="unit-list">
                <li>Length, mass, temperature, time, volume, energy, pressure, and speed</li>
                <li>Electricity, illumination, luminous intensity, radiation, magnetism, force, and sound level</li>
                <li>Meter, kilometer, inch, foot, mile, kilogram, pound, joule, calorie, pascal, newton, dyne, lbf, kgf, and more</li>
            </ul>
        </section>
    </main>

    <aside class="settings-window" id="settingsWindow" role="dialog" aria-modal="true" aria-label="Settings panel">
        <div class="settings-header">
            <h3>Settings</h3>
            <button class="settings-close" id="settingsCloseButton" type="button" aria-label="Close settings">Close</button>
        </div>

        <div class="settings-section">
            <div class="settings-label">Appearance</div>
            <div class="settings-options" role="tablist" aria-label="Theme selection">
                <button class="settings-option active" data-theme="light" type="button">Light</button>
                <button class="settings-option" data-theme="dark" type="button">Dark</button>
                <button class="settings-option" data-theme="system" type="button">System</button>
            </div>
        </div>

        <div class="settings-section">
            <div class="settings-label">Quick actions</div>
            <div class="settings-actions" role="group" aria-label="History and help actions">
                <button class="settings-action" id="historyActionButton" type="button">History</button>
                <button class="settings-action" id="helpActionButton" type="button">Help</button>
            </div>
        </div>
    </aside>

    <aside class="dialog-window" id="historyWindow" role="dialog" aria-modal="true" aria-label="History panel">
        <div class="settings-header">
            <h3>History</h3>
            <button class="settings-close" id="historyCloseButton" type="button" aria-label="Close history">Close</button>
        </div>
        <div class="dialog-body">
            <div id="historyList" class="history-list" aria-live="polite"></div>
        </div>
    </aside>

    <aside class="dialog-window" id="helpWindow" role="dialog" aria-modal="true" aria-label="Help panel">
        <div class="settings-header">
            <h3>Help</h3>
            <button class="settings-close" id="helpCloseButton" type="button" aria-label="Close help">Close</button>
        </div>
        <div class="dialog-body">
            <p>Use Calculator mode for arithmetic and Converter mode for unit conversion between supported categories.</p>
            <p>Pick a category, choose the units to convert, and use the result box for quick calculations.</p>
            <p>Theme changes persist in your browser, and the history window keeps a recent log of your actions.</p>
        </div>
    </aside>

    <script>
        const categoryConfig = {{ category_config|tojson }};
        const temperatureUnits = ["Kelvin", "Celsius", "Fahrenheit", "Rankine"];

        const appShell = document.getElementById("appShell");
        const settingsButton = document.getElementById("settingsButton");
        const settingsWindow = document.getElementById("settingsWindow");
        const settingsCloseButton = document.getElementById("settingsCloseButton");
        const historyButton = document.getElementById("historyButton");
        const historyWindow = document.getElementById("historyWindow");
        const historyCloseButton = document.getElementById("historyCloseButton");
        const historyList = document.getElementById("historyList");
        const helpButton = document.getElementById("helpActionButton");
        const helpWindow = document.getElementById("helpWindow");
        const helpCloseButton = document.getElementById("helpCloseButton");
        const calculatorModeButton = document.getElementById("calculatorModeButton");
        const converterModeButton = document.getElementById("converterModeButton");
        const settingsThemeButtons = Array.from(document.querySelectorAll(".settings-option"));
        const historyActionButton = document.getElementById("historyActionButton");

        const calculatorValue1 = document.getElementById("calculatorValue1");
        const calculatorValue2 = document.getElementById("calculatorValue2");
        const calculatorOperation = document.getElementById("calculatorOperation");
        const calculateButton = document.getElementById("calculateButton");
        const calculatorResult = document.getElementById("calculatorResult");

        const categorySelect = document.getElementById("category");
        const fromUnitSelect = document.getElementById("fromUnit");
        const toUnitSelect = document.getElementById("toUnit");
        const valueInput = document.getElementById("value");
        const resultBox = document.getElementById("result");
        const convertButton = document.getElementById("convertButton");
        const categoryToggle = document.getElementById("categoryToggle");
        const categoryLabel = document.getElementById("categoryLabel");
        const fromUnitToggle = document.getElementById("fromUnitToggle");
        const fromUnitLabel = document.getElementById("fromUnitLabel");
        const toUnitToggle = document.getElementById("toUnitToggle");
        const toUnitLabel = document.getElementById("toUnitLabel");
        const themeButtons = {};
        const dropdownState = {};

        function getStoredTheme() {
            try {
                return window.localStorage.getItem("cc-theme") || "system";
            } catch (error) {
                return "system";
            }
        }

        function getStoredSettingsOpen() {
            try {
                return window.localStorage.getItem("cc-settings-open") === "true";
            } catch (error) {
                return false;
            }
        }

        function getSystemTheme() {
            return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        }

        function applyTheme(theme) {
            const resolvedTheme = theme === "system" ? getSystemTheme() : theme;
            document.body.dataset.theme = theme;
            document.body.dataset.resolvedTheme = resolvedTheme;

            Object.entries(themeButtons).forEach(([name, button]) => {
                if (button) {
                    button.classList.toggle("active", name === theme);
                }
            });

            settingsThemeButtons.forEach((button) => {
                const selected = button.dataset.theme === theme;
                button.classList.toggle("active", selected);
                button.setAttribute("aria-pressed", selected ? "true" : "false");
            });
        }

        function setTheme(theme) {
            try {
                window.localStorage.setItem("cc-theme", theme);
            } catch (error) {
                // Ignore storage failures and keep the in-memory theme.
            }

            applyTheme(theme);
        }

        function setWindowState(windowElement, triggerButton, forceOpen) {
            const open = typeof forceOpen === "boolean" ? forceOpen : !windowElement.classList.contains("open");
            const allWindows = [settingsWindow, historyWindow, helpWindow].filter(Boolean);

            allWindows.forEach((item) => {
                if (item && item !== windowElement) {
                    item.classList.remove("open");
                }
            });

            if (windowElement) {
                windowElement.classList.toggle("open", open);
            }

            if (triggerButton) {
                triggerButton.setAttribute("aria-expanded", String(open));
            }

            if (settingsWindow && settingsButton) {
                settingsButton.setAttribute("aria-expanded", String(settingsWindow.classList.contains("open")));
            }
            if (historyWindow && historyButton) {
                historyButton.setAttribute("aria-expanded", String(historyWindow.classList.contains("open")));
            }
            if (helpWindow && helpButton) {
                helpButton.setAttribute("aria-expanded", String(helpWindow.classList.contains("open")));
            }
        }

        function toggleSettingsWindow(forceOpen) {
            const open = typeof forceOpen === "boolean" ? forceOpen : !settingsWindow.classList.contains("open");
            setWindowState(settingsWindow, settingsButton, open);

            try {
                window.localStorage.setItem("cc-settings-open", String(open));
            } catch (error) {
                // Ignore storage failures; visible state is best-effort.
            }
        }

        function toggleHistoryWindow(forceOpen) {
            const open = typeof forceOpen === "boolean" ? forceOpen : !historyWindow.classList.contains("open");
            setWindowState(historyWindow, historyButton, open);
        }

        function toggleHelpWindow(forceOpen) {
            const open = typeof forceOpen === "boolean" ? forceOpen : !helpWindow.classList.contains("open");
            setWindowState(helpWindow, helpButton, open);
        }

        function formatNumber(value) {
            if (!Number.isFinite(value)) {
                return "Unable to convert";
            }

            const absoluteValue = Math.abs(value);
            if (absoluteValue !== 0 && (absoluteValue >= 1e9 || absoluteValue < 1e-6)) {
                return value.toExponential(8);
            }

            return Number(value.toFixed(8)).toString();
        }

        function setMode(mode) {
            if (!appShell) {
                return;
            }

            appShell.dataset.mode = mode;
            calculatorModeButton.classList.toggle("active", mode === "calculator");
            converterModeButton.classList.toggle("active", mode === "converter");
        }

        function calculateValue() {
            const value1 = Number(calculatorValue1.value);
            const value2 = Number(calculatorValue2.value);
            const operation = calculatorOperation.value;

            if (Number.isNaN(value1) || Number.isNaN(value2)) {
                calculatorResult.innerHTML = "<strong>Result unavailable</strong><p>Enter valid numbers and try again.</p>";
                return;
            }

            let result = 0;

            if (operation === "add") {
                result = value1 + value2;
            } else if (operation === "subtract") {
                result = value1 - value2;
            } else if (operation === "multiply") {
                result = value1 * value2;
            } else if (operation === "divide") {
                if (value2 === 0) {
                    calculatorResult.innerHTML = "<strong>Result unavailable</strong><p>Cannot divide by zero.</p>";
                    return;
                }

                result = value1 / value2;
            }

            calculatorResult.innerHTML = `<strong>${formatNumber(result)}</strong><p>${value1} ${operation} ${value2} = ${formatNumber(result)}</p>`;
        }

        function closeDropdowns(exceptKey = null) {
            Object.entries(dropdownState).forEach(([key, dropdown]) => {
                if (dropdown && key !== exceptKey) {
                    dropdown.root.classList.remove("open");
                    dropdown.toggle.setAttribute("aria-expanded", "false");
                }
            });
        }

        function syncDropdownDisplay(select) {
            const dropdown = dropdownState[select.id];
            if (!dropdown) {
                return;
            }

            const options = Array.from(select.options).map((option) => option.value);
            dropdown.menu.innerHTML = "";

            options.forEach((value) => {
                const optionButton = document.createElement("button");
                optionButton.type = "button";
                optionButton.className = "dropdown-option";
                optionButton.textContent = value;
                optionButton.setAttribute("role", "option");
                optionButton.setAttribute("aria-selected", value === select.value ? "true" : "false");

                if (value === select.value) {
                    optionButton.classList.add("selected");
                }

                optionButton.addEventListener("click", (event) => {
                    event.stopPropagation();
                    select.value = value;
                    dropdown.label.textContent = value;
                    dropdown.menu.querySelectorAll(".dropdown-option").forEach((button) => {
                        const selected = button === optionButton;
                        button.classList.toggle("selected", selected);
                        button.setAttribute("aria-selected", selected ? "true" : "false");
                    });
                    closeDropdowns();

                    if (select.id === "category") {
                        updateUnitSelectors();
                        convertValue();
                    } else {
                        convertValue();
                    }
                });

                dropdown.menu.appendChild(optionButton);
            });

            dropdown.label.textContent = select.value || options[0] || "";
        }

        function bindDropdown(select, dropdownRoot, toggle, label, menu) {
            dropdownState[select.id] = { root: dropdownRoot, toggle, label, menu };
            toggle.addEventListener("click", (event) => {
                event.stopPropagation();
                const isOpen = dropdownRoot.classList.contains("open");
                closeDropdowns(select.id);
                if (!isOpen) {
                    dropdownRoot.classList.add("open");
                    toggle.setAttribute("aria-expanded", "true");
                }
            });

            document.addEventListener("click", (event) => {
                if (!dropdownRoot.contains(event.target)) {
                    dropdownRoot.classList.remove("open");
                    toggle.setAttribute("aria-expanded", "false");
                }
            });

            syncDropdownDisplay(select);
        }

        function setOptions(select, options) {
            if (!select) {
                return;
            }

            select.innerHTML = "";
            options.forEach((option, index) => {
                const optionElement = document.createElement("option");
                optionElement.value = option;
                optionElement.textContent = option;
                if (index === 0) {
                    optionElement.selected = true;
                }
                select.appendChild(optionElement);
            });

            if (select.id in dropdownState) {
                syncDropdownDisplay(select);
            }
        }

        function getUnitList(category) {
            const config = categoryConfig[category];
            if (!config) {
                return [];
            }

            if (config.type === "temperature") {
                return temperatureUnits;
            }

            return config.type === "linear" ? Object.keys(config.units) : config.units;
        }

        function updateUnitSelectors() {
            const category = categorySelect.value;
            const units = getUnitList(category);
            setOptions(fromUnitSelect, units);
            setOptions(toUnitSelect, units);

            if (units.length > 1) {
                toUnitSelect.selectedIndex = 1;
                syncDropdownDisplay(toUnitSelect);
            }
        }

        function convertTemperature(value, fromUnit, toUnit) {
            const toKelvin = {
                Kelvin: (input) => input,
                Celsius: (input) => input + 273.15,
                Fahrenheit: (input) => ((input + 459.67) * 5) / 9,
                Rankine: (input) => (input * 5) / 9,
            };

            const fromKelvin = {
                Kelvin: (input) => input,
                Celsius: (input) => input - 273.15,
                Fahrenheit: (input) => (input * 9) / 5 - 459.67,
                Rankine: (input) => (input * 9) / 5,
            };

            return fromKelvin[toUnit](toKelvin[fromUnit](value));
        }

        function saveHistoryEntry(valueText, resultText) {
            const payload = {
                value: valueText,
                result: resultText,
                timestamp: new Date().toLocaleString(),
            };

            fetch("/history", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            }).catch(() => {
                // Ignore network errors; the page should keep working.
            }).then(() => loadHistory());
        }

        function isValidConversion(category, fromUnit, toUnit) {
            const config = categoryConfig[category];
            if (!config || !fromUnit || !toUnit) {
                return false;
            }

            if (config.type === "temperature") {
                return temperatureUnits.includes(fromUnit) && temperatureUnits.includes(toUnit);
            }

            if (config.type === "linear") {
                return Object.prototype.hasOwnProperty.call(config.units, fromUnit) && Object.prototype.hasOwnProperty.call(config.units, toUnit);
            }

            if (config.type === "reference") {
                return fromUnit === toUnit && config.units.includes(fromUnit);
            }

            return false;
        }

        function convertValue() {
            const category = categorySelect.value;
            const value = Number(valueInput.value);
            const fromUnit = fromUnitSelect.value;
            const toUnit = toUnitSelect.value;
            const config = categoryConfig[category];

            if (!config || Number.isNaN(value) || !isValidConversion(category, fromUnit, toUnit)) {
                resultBox.innerHTML = "<strong>Conversion unavailable</strong><p>Choose two compatible units from the same category.</p>";
                return;
            }

            if (config.type === "temperature") {
                const converted = convertTemperature(value, fromUnit, toUnit);
                const summary = `${formatNumber(converted)} ${toUnit}`;
                const description = `${value} ${fromUnit} = ${formatNumber(converted)} ${toUnit}`;
                resultBox.innerHTML = `<strong>${summary}</strong><p>${description}</p>`;
                return;
            }

            if (config.type === "linear") {
                const fromFactor = config.units[fromUnit];
                const toFactor = config.units[toUnit];
                const converted = value * fromFactor / toFactor;
                const summary = `${formatNumber(converted)} ${toUnit}`;
                const description = `${value} ${fromUnit} = ${formatNumber(converted)} ${toUnit}`;
                resultBox.innerHTML = `<strong>${summary}</strong><p>${description}</p>`;
                return;
            }

            resultBox.innerHTML = `<strong>${value} ${fromUnit}</strong><p>${category} is listed as a reference quantity. Select the same unit to keep the value unchanged.</p>`;
        }

        function convertAndRecordHistory() {
            const category = categorySelect.value;
            const value = Number(valueInput.value);
            const fromUnit = fromUnitSelect.value;
            const toUnit = toUnitSelect.value;
            const config = categoryConfig[category];

            if (!config || Number.isNaN(value) || !isValidConversion(category, fromUnit, toUnit)) {
                return;
            }

            if (config.type === "temperature") {
                const converted = convertTemperature(value, fromUnit, toUnit);
                const summary = `${formatNumber(converted)} ${toUnit}`;
                const description = `${value} ${fromUnit} = ${formatNumber(converted)} ${toUnit}`;
                resultBox.innerHTML = `<strong>${summary}</strong><p>${description}</p>`;
                saveHistoryEntry(`${value} ${fromUnit} to ${toUnit}`, description);
                return;
            }

            if (config.type === "linear") {
                const fromFactor = config.units[fromUnit];
                const toFactor = config.units[toUnit];
                const converted = value * fromFactor / toFactor;
                const summary = `${formatNumber(converted)} ${toUnit}`;
                const description = `${value} ${fromUnit} = ${formatNumber(converted)} ${toUnit}`;
                resultBox.innerHTML = `<strong>${summary}</strong><p>${description}</p>`;
                saveHistoryEntry(`${value} ${fromUnit} to ${toUnit}`, description);
                return;
            }

            resultBox.innerHTML = `<strong>${value} ${fromUnit}</strong><p>${category} is listed as a reference quantity. Select the same unit to keep the value unchanged.</p>`;
        }

        function renderHistoryEntries(items) {
            if (!historyList) {
                return;
            }

            const entries = Array.isArray(items) && items.length ? items : [{ value: "No conversion history yet.", result: "Start converting to build your log.", timestamp: "" }];
            historyList.innerHTML = entries
                .slice(0, 8)
                .map((entry) => {
                    const value = entry && typeof entry.value === "string" ? entry.value : "Recent conversion";
                    const result = entry && typeof entry.result === "string" && entry.result.trim() ? entry.result : "Saved result";
                    const stamp = entry && typeof entry.timestamp === "string" && entry.timestamp ? entry.timestamp : "Just now";
                    return `<li class="history-item"><strong>${value}</strong><span>${result}</span><small>${stamp}</small></li>`;
                })
                .join("");
        }

        async function loadHistory() {
            try {
                const response = await fetch("/history");
                if (!response.ok) {
                    renderHistoryEntries([]);
                    return;
                }

                const payload = await response.json();
                renderHistoryEntries(Array.isArray(payload.items) ? payload.items : payload);
            } catch (error) {
                renderHistoryEntries([]);
            }
        }

        function populateCategories() {
            const categories = Object.keys(categoryConfig);
            setOptions(categorySelect, categories);
        }

        if (categorySelect && fromUnitSelect && toUnitSelect && valueInput && resultBox && convertButton) {
            bindDropdown(categorySelect, document.getElementById("categoryDropdown"), categoryToggle, categoryLabel, document.getElementById("categoryMenu"));
            bindDropdown(fromUnitSelect, document.getElementById("fromUnitDropdown"), fromUnitToggle, fromUnitLabel, document.getElementById("fromUnitMenu"));
            bindDropdown(toUnitSelect, document.getElementById("toUnitDropdown"), toUnitToggle, toUnitLabel, document.getElementById("toUnitMenu"));

            settingsButton.addEventListener("click", () => toggleSettingsWindow());
            settingsCloseButton.addEventListener("click", () => toggleSettingsWindow(false));
            historyButton.addEventListener("click", () => toggleHistoryWindow());
            historyActionButton.addEventListener("click", () => toggleHistoryWindow());
            historyCloseButton.addEventListener("click", () => toggleHistoryWindow(false));
            helpButton.addEventListener("click", () => toggleHelpWindow());
            helpCloseButton.addEventListener("click", () => toggleHelpWindow(false));
            document.addEventListener("click", (event) => {
                const clickedInsideSettings = settingsWindow && settingsWindow.contains(event.target);
                const clickedInsideHistory = historyWindow && historyWindow.contains(event.target);
                const clickedInsideHelp = helpWindow && helpWindow.contains(event.target);
                const clickedHistoryTrigger = historyButton && historyButton.contains(event.target);
                const clickedSettingsTrigger = settingsButton && settingsButton.contains(event.target);
                const clickedHelpTrigger = helpButton && helpButton.contains(event.target);
                const clickedHistoryAction = historyActionButton && historyActionButton.contains(event.target);

                if (!clickedInsideSettings && !clickedInsideHistory && !clickedInsideHelp && !clickedHistoryTrigger && !clickedSettingsTrigger && !clickedHelpTrigger && !clickedHistoryAction) {
                    toggleSettingsWindow(false);
                    toggleHistoryWindow(false);
                    toggleHelpWindow(false);
                }
            });

            calculatorModeButton.addEventListener("click", () => setMode("calculator"));
            converterModeButton.addEventListener("click", () => setMode("converter"));
            settingsThemeButtons.forEach((button) => {
                button.addEventListener("click", () => setTheme(button.dataset.theme));
            });
            calculateButton.addEventListener("click", calculateValue);
            calculatorValue1.addEventListener("input", calculateValue);
            calculatorValue2.addEventListener("input", calculateValue);
            calculatorOperation.addEventListener("change", calculateValue);

            populateCategories();
            updateUnitSelectors();

            categorySelect.addEventListener("change", () => {
                updateUnitSelectors();
                convertValue();
            });

            convertButton.addEventListener("click", convertAndRecordHistory);
            valueInput.addEventListener("input", convertValue);
            fromUnitSelect.addEventListener("change", convertValue);
            toUnitSelect.addEventListener("change", convertValue);

            const storedTheme = getStoredTheme();
            applyTheme(storedTheme);
            toggleSettingsWindow(getStoredSettingsOpen());
            settingsButton.setAttribute("aria-expanded", String(settingsWindow.classList.contains("open")));
            loadHistory();
            setMode("converter");
            calculateValue();
            convertValue();

            if (window.matchMedia) {
                const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
                mediaQuery.addEventListener("change", () => {
                    if (getStoredTheme() === "system") {
                        applyTheme("system");
                    }
                });
            }
        }
    </script>
</body>
</html>
"""


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
    return render_template_string(PAGE_TEMPLATE, category_config=UNIT_CATEGORIES)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

