from flask import Flask, render_template_string

app = Flask(__name__)

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
        "type": "reference",
        "units": ["Newton"],
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
            display: grid;
            place-items: center;
            padding: 24px;
        }

        .shell {
            width: min(100%, 1040px);
            display: grid;
            gap: 20px;
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
            overflow: hidden;
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

        .theme-switch {
            display: inline-flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: flex-end;
            margin-top: 12px;
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

            <div class="mode-switch" role="tablist" aria-label="App mode">
                <button class="mode-button active" id="calculatorModeButton" type="button">Calculator</button>
                <button class="mode-button" id="converterModeButton" type="button">Converter</button>
            </div>

            <div>
                <div class="mode-switch theme-switch" role="tablist" aria-label="Theme mode">
                    <button class="mode-button active" id="lightThemeButton" type="button">Light</button>
                    <button class="mode-button" id="darkThemeButton" type="button">Dark</button>
                    <button class="mode-button" id="systemThemeButton" type="button">System</button>
                </div>
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
                <select id="category"></select>
            </div>

            <div class="field">
                <label for="value">Value</label>
                <input id="value" type="number" inputmode="decimal" value="1" />
            </div>

            <div class="grid-2">
                <div class="field">
                    <label for="fromUnit">From</label>
                    <select id="fromUnit"></select>
                </div>
                <div class="field">
                    <label for="toUnit">To</label>
                    <select id="toUnit"></select>
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
                The converter includes every unit named in your list. Where a unit is a reference quantity rather than a
                directly convertible scale, it is still available in the catalog.
            </p>
            <ul class="unit-list">
                <li>Length, mass, temperature, time, volume, energy, pressure, and speed</li>
                <li>Electricity, illumination, luminous intensity, radiation, magnetism, force, and sound level</li>
                <li>Meter, kilometer, inch, foot, mile, kilogram, pound, joule, calorie, pascal, newton, tesla, decibel, and more</li>
            </ul>
        </section>
    </main>

    <script>
        const categoryConfig = {{ category_config|tojson }};
        const temperatureUnits = ["Kelvin", "Celsius", "Fahrenheit", "Rankine"];

        const appShell = document.getElementById("appShell");
        const calculatorModeButton = document.getElementById("calculatorModeButton");
        const converterModeButton = document.getElementById("converterModeButton");
        const lightThemeButton = document.getElementById("lightThemeButton");
        const darkThemeButton = document.getElementById("darkThemeButton");
        const systemThemeButton = document.getElementById("systemThemeButton");

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
        const themeButtons = {
            light: lightThemeButton,
            dark: darkThemeButton,
            system: systemThemeButton,
        };

        function getStoredTheme() {
            try {
                return window.localStorage.getItem("cc-theme") || "system";
            } catch (error) {
                return "system";
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
        }

        function setTheme(theme) {
            try {
                window.localStorage.setItem("cc-theme", theme);
            } catch (error) {
                // Ignore storage failures and keep the in-memory theme.
            }

            applyTheme(theme);
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

        function convertValue() {
            const category = categorySelect.value;
            const value = Number(valueInput.value);
            const fromUnit = fromUnitSelect.value;
            const toUnit = toUnitSelect.value;
            const config = categoryConfig[category];

            if (!config || Number.isNaN(value)) {
                resultBox.innerHTML = "<strong>Result unavailable</strong><p>Enter a valid value and try again.</p>";
                return;
            }

            if (config.type === "temperature") {
                const converted = convertTemperature(value, fromUnit, toUnit);
                resultBox.innerHTML = `<strong>${formatNumber(converted)} ${toUnit}</strong><p>${value} ${fromUnit} = ${formatNumber(converted)} ${toUnit}</p>`;
                return;
            }

            if (config.type === "linear") {
                const fromFactor = config.units[fromUnit];
                const toFactor = config.units[toUnit];
                const converted = value * fromFactor / toFactor;
                resultBox.innerHTML = `<strong>${formatNumber(converted)} ${toUnit}</strong><p>${value} ${fromUnit} = ${formatNumber(converted)} ${toUnit}</p>`;
                return;
            }

            resultBox.innerHTML = `<strong>${value} ${fromUnit}</strong><p>${category} is listed as a reference quantity. Select the same unit to keep the value unchanged.</p>`;
        }

        function populateCategories() {
            const categories = Object.keys(categoryConfig);
            setOptions(categorySelect, categories);
        }

        if (categorySelect && fromUnitSelect && toUnitSelect && valueInput && resultBox && convertButton) {
            calculatorModeButton.addEventListener("click", () => setMode("calculator"));
            converterModeButton.addEventListener("click", () => setMode("converter"));
            lightThemeButton.addEventListener("click", () => setTheme("light"));
            darkThemeButton.addEventListener("click", () => setTheme("dark"));
            systemThemeButton.addEventListener("click", () => setTheme("system"));
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

            convertButton.addEventListener("click", convertValue);
            valueInput.addEventListener("input", convertValue);
            fromUnitSelect.addEventListener("change", convertValue);
            toUnitSelect.addEventListener("change", convertValue);

            applyTheme(getStoredTheme());
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


@app.route("/")
def home():
    return render_template_string(PAGE_TEMPLATE, category_config=UNIT_CATEGORIES)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

