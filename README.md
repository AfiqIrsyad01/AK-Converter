# AK-Converter | AllInOne Unit Converter (PyQt6)

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
![PyQt6](https://img.shields.io/badge/PyQt-6-41CD52?logo=qt&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)
![Platforms](https://img.shields.io/badge/Platforms-Windows%20%7C%20macOS%20%7C%20Linux-informational)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)

A modern, cross‑platform desktop app for quick conversions across physical, digital, health/education, finance, and miscellaneous units. Built with PyQt6. Most converters work offline; currency conversion updates live from a free API.

- Clean dark UI with rounded corners, shadows, and consistent controls
- Input validation, Enter-to-convert, and Swap buttons
- Currency support for many fiat and crypto (cached with refresh)

![Screenshot](image.png)

## Features
- Physical Units: Length, Mass, Temperature, Volume, Area, Speed, Energy, Power, Pressure, Angle, Density
- Digital Units: Storage, Data Rate, Time, Decimal → Hex, RGB → Hex
- Health/Education: BMI (kg/lb, m/cm/in), CGPA, Grade Converter, Age Calculator, Date Difference, BMR/TDEE, Tip Calculator, Discount Calculator
- Finance: Currency Converter (auto/refresh, swap, many currencies incl. BTC/ETH)
- Miscellaneous: Frequency, Force, Torque, Viscosity, Fuel Efficiency (MPG ↔ L/100km), Illuminance

Extras:
- Most conversions supported with Swap, Enter-to-convert, and live updates on selection changes
- Robust input validation and helpful messages
- Currency rates are cached for 30 minutes; refresh anytime

## Tech
- Python 3.9+
- PyQt6
- requests (optional, for currency API)

## Getting Started
Clone the repo:
```bash
git clone https://github.com/AfiqIrsyad01/AK-Converter.git
cd AK-Converter
```

Install dependencies:
- If you have a requirements.txt:
```bash
pip install -r requirements.txt
```
- or install directly:
```bash
pip install PyQt6 requests
```

Run:
```bash
python ak-converter.py
```

## Currency Conversion
- Uses exchangerate.host (free, no API key required)
- Works for common fiat and crypto like BTC/ETH
- Caches rates for 30 minutes; click “Refresh Rates” to force update
- If requests isn’t installed or there’s no internet, currency conversion will be unavailable

## Usage Tips
- Press Enter in any input to convert immediately
- Click Swap to swap from/to units
- Currency converter auto-converts on selection changes; use Refresh Rates if needed
- BMI supports kg/lb and m/cm/in; includes category (Underweight/Normal/Overweight/Obesity)

## Supported Units (quick reference)
Examples (not exhaustive):
- Length: m, cm, mm, km, inch, foot, yard, mile, nautical mile
- Mass: mg, g, kg, tonne, ounce, pound
- Volume: m³, liter, milliliter, US gallon/quart/pint/cup
- Area: m², cm², km², inch², ft², acre, hectare
- Speed: m/s, km/h, mph, knot
- Energy: joule, kJ, calorie, kcal, Wh, kWh, eV
- Power: watt, kW, horsepower (metric/US)
- Pressure: pascal, bar, atmosphere, PSI, torr
- Angle: radian, degree, gradian
- Storage: bit/byte, KB/MB/GB/TB (binary units included in data rate)
- Data Rate: bps, Kbps, Mbps, Gbps, KiB/s, MiB/s, GiB/s
- Fuel Efficiency: MPG (US), L/100km
- Illuminance: lux, foot-candle

## Troubleshooting
- Qt platform plugin errors on Linux (xcb):
  - Install missing system packages: e.g., on Debian/Ubuntu: sudo apt-get install libxcb-xinerama0 libxcb-cursor0
- Currency conversion fails:
  - Check your internet connection/firewall
  - Click “Refresh Rates”
  - Ensure requests is installed: pip install requests
- Nothing shows when launching:
  - Ensure you’re running python main.py with Python 3.9+
  - If you heavily modified effects/animations, ensure only one graphics effect per widget is used

## Roadmap
- Light theme toggle
- Unit search/filter
- Custom favorites section
- Historical currency rates
- Localization (multiple languages)

## Acknowledgments
- Currency rates by exchangerate.host
- Built with PyQt6
