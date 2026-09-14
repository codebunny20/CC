const categoryConfig = window.APP_CONFIG;
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
