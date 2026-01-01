import os
import pandas as pd


def unitisation_process(
    opening_units: float,
    opening_nav_per_unit: float,
    transactions_file: str,
    nav_per_unit_by_date: dict,
):
    """
    Unitisation logic (simplified, audit-friendly):
    - Subscriptions create units = Amount / NAV_per_unit_on_date
    - Redemptions cancel units = Amount / NAV_per_unit_on_date
    - Tracks investor units and total units over time

    nav_per_unit_by_date: {"YYYY-MM-DD": nav_per_unit}
    """

    tx = pd.read_csv(transactions_file)
    tx["Date"] = pd.to_datetime(tx["Date"]).dt.strftime("%Y-%m-%d")

    # Validate required columns
    required = {"Date", "Investor", "Type", "Amount_Base"}
    missing = required - set(tx.columns)
    if missing:
        raise ValueError(f"Missing columns in transactions file: {missing}")

    # Normalise Type values
    tx["Type"] = tx["Type"].str.strip().str.lower()
    if not set(tx["Type"]).issubset({"subscription", "redemption"}):
        raise ValueError("Type must be 'Subscription' or 'Redemption'")

    # Sort by date for clean processing
    tx = tx.sort_values(["Date", "Investor"]).reset_index(drop=True)

    investor_units = {}  # Investor -> units
    total_units = float(opening_units)

    rows = []

    for _, r in tx.iterrows():
        date = r["Date"]
        investor = r["Investor"]
        tx_type = r["Type"]
        amount = float(r["Amount_Base"])

        if date not in nav_per_unit_by_date:
            raise ValueError(f"NAV per unit missing for date {date} in nav_per_unit_by_date")

        navpu = float(nav_per_unit_by_date[date])
        if navpu <= 0:
            raise ValueError(f"NAV per unit must be > 0 for date {date}")

        units_delta = amount / navpu

        if investor not in investor_units:
            investor_units[investor] = 0.0

        if tx_type == "subscription":
            investor_units[investor] += units_delta
            total_units += units_delta
            signed_units = units_delta
        else:  # redemption
            # Ensure investor has enough units (simple control)
            if investor_units[investor] + 1e-12 < units_delta:
                raise ValueError(
                    f"Redemption exceeds available units for {investor} on {date}. "
                    f"Has {investor_units[investor]:.6f}, trying to redeem {units_delta:.6f}"
                )
            investor_units[investor] -= units_delta
            total_units -= units_delta
            signed_units = -units_delta

        rows.append({
            "Date": date,
            "Investor": investor,
            "Type": "Subscription" if tx_type == "subscription" else "Redemption",
            "Amount_Base": round(amount, 2),
            "NAV_Per_Unit": round(navpu, 6),
            "Units_Change": round(signed_units, 6),
            "Investor_Units_After": round(investor_units[investor], 6),
            "Total_Units_After": round(total_units, 6),
        })

    ledger = pd.DataFrame(rows)

    investor_summary = (
        pd.DataFrame([{"Investor": k, "Units": v} for k, v in investor_units.items()])
        .sort_values("Investor")
        .reset_index(drop=True)
    )

    totals = pd.DataFrame([{
        "Opening_Units": round(opening_units, 6),
        "Opening_NAV_Per_Unit": round(opening_nav_per_unit, 6),
        "Closing_Units": round(total_units, 6),
    }])

    return ledger, investor_summary, totals


def main():
    os.makedirs("outputs", exist_ok=True)

    # Opening fund state (edit as needed)
    opening_units = 100000.0
    opening_nav_per_unit = 1.000000

    # NAV per unit used for unit pricing on each dealing date
    # (In real operations this comes from the NAV pack for that date.)
    nav_per_unit_by_date = {
        "2026-01-02": 1.012500,
        "2026-01-03": 1.008000,
        "2026-01-04": 1.015200,
    }

    ledger, investor_summary, totals = unitisation_process(
        opening_units=opening_units,
        opening_nav_per_unit=opening_nav_per_unit,
        transactions_file="sample_investor_transactions.csv",
        nav_per_unit_by_date=nav_per_unit_by_date,
    )

    ledger.to_csv("outputs/unitisation_ledger.csv", index=False)
    investor_summary.to_csv("outputs/investor_units_summary.csv", index=False)
    totals.to_csv("outputs/unitisation_totals.csv", index=False)

    print("Saved outputs:")
    print("- outputs/unitisation_ledger.csv")
    print("- outputs/investor_units_summary.csv")
    print("- outputs/unitisation_totals.csv\n")

    print("Closing Units:", float(totals.loc[0, "Closing_Units"]))


if __name__ == "__main__":
    main()
