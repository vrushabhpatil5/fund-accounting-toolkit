import os
import pandas as pd


def calculate_nav(positions_file: str, liabilities_file: str, units_outstanding: float, base_ccy: str = "USD"):
    # Load positions
    pos = pd.read_csv(positions_file)

    # Validate required columns
    required_pos_cols = {"Instrument", "Quantity", "Price", "Base_CCY", "FX_to_Base"}
    if not required_pos_cols.issubset(pos.columns):
        missing = required_pos_cols - set(pos.columns)
        raise ValueError(f"Missing columns in positions file: {missing}")

    # Calculate market value in base currency
    pos["Market_Value_Base"] = pos["Quantity"] * pos["Price"] * pos["FX_to_Base"]

    total_assets = float(pos["Market_Value_Base"].sum())

    # Load liabilities
    liab = pd.read_csv(liabilities_file)

    required_liab_cols = {"Liability", "Amount", "Base_CCY"}
    if not required_liab_cols.issubset(liab.columns):
        missing = required_liab_cols - set(liab.columns)
        raise ValueError(f"Missing columns in liabilities file: {missing}")

    total_liabilities = float(liab["Amount"].sum())

    net_assets = total_assets - total_liabilities

    if units_outstanding <= 0:
        raise ValueError("Units outstanding must be greater than 0.")

    nav_per_unit = net_assets / units_outstanding

    # Output tables
    summary = pd.DataFrame([{
        "Base_CCY": base_ccy,
        "Total_Assets": round(total_assets, 2),
        "Total_Liabilities": round(total_liabilities, 2),
        "Net_Assets": round(net_assets, 2),
        "Units_Outstanding": units_outstanding,
        "NAV_Per_Unit": round(nav_per_unit, 6)
    }])

    return pos, liab, summary


def main():
    os.makedirs("outputs", exist_ok=True)

    positions_file = "sample_fund_positions.csv"
    liabilities_file = "sample_liabilities.csv"

    # Example: units outstanding (edit as needed)
    units_outstanding = 100000.0

    pos, liab, summary = calculate_nav(
        positions_file=positions_file,
        liabilities_file=liabilities_file,
        units_outstanding=units_outstanding,
        base_ccy="USD"
    )

    # Save outputs (Excel-friendly)
    pos.to_csv("outputs/nav_positions_valued.csv", index=False)
    liab.to_csv("outputs/nav_liabilities.csv", index=False)
    summary.to_csv("outputs/nav_summary.csv", index=False)

    print("Saved outputs:")
    print("- outputs/nav_positions_valued.csv")
    print("- outputs/nav_liabilities.csv")
    print("- outputs/nav_summary.csv\n")

    print("NAV Summary:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
