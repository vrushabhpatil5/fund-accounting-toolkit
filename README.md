# Fund Accounting Toolkit

A Python-based toolkit demonstrating core **fund accounting processes**
using simple, transparent models and Excel-friendly outputs.

This project focuses on the **operational side of asset management**,
including NAV calculation, unitisation, and expense accruals,
rather than corporate valuation theory.

---

## Scope
This toolkit is designed to reflect how funds are processed and reported
in real-world fund accounting and NAV operations teams.

---

## Modules

### 1) NAV Calculation (Core Module)
- Market value calculation for fund positions
- FX conversion to base currency
- Liability and expense accrual handling
- Net Assets and NAV per unit calculation

---

## Project Structure
'''
fund-accounting-toolkit/
├── nav_calculation.py
│
├── sample_fund_positions.csv
├── sample_liabilities.csv
│
├── outputs/
│ ├── nav_positions_valued.csv
│ ├── nav_liabilities.csv
│ └── nav_summary.csv
│
├── requirements.txt
└── README.md
'''


---

## How to Run

### Install dependencies
```bash
pip install -r requirements.txt
'''
