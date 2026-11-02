
import pandas as pd

# Load real district-level crime data
df = pd.read_csv("data/ncrb_crime_data_2022.csv")

# Find Jalandhar
jalandhar = df[
    df["dis"].astype(str).str.contains(
        "Jalandhar", case=False, na=False
    )
]

if jalandhar.empty:
    print("Jalandhar data not found.")
else:
    row = jalandhar.iloc[0]

    # Prepare selected statistics
    crime_data = {
        "Crime Category": [
            "Reported rape cases",
            "Cruelty-related cases",
            "Dowry deaths",
            "Acid attacks",
            "Kidnapping/abduction cases",
        ],
        "2022": [
            row.get("totrape22"),
            row.get("crlhus22"),
            row.get("dwydeath22"),
            row.get("acidatt22"),
            row.get("totkidabd22"),
        ],
        "2023": [
            row.get("totrape23"),
            row.get("crlhus23"),
            row.get("dwydeath23"),
            row.get("acidatt23"),
            row.get("totkidabd23"),
        ],
        "2024": [
            row.get("totrape24"),
            row.get("crlhus24"),
            row.get("dwydeath24"),
            row.get("acidatt24"),
            row.get("totkidabd24"),
        ],
    }

    report = pd.DataFrame(crime_data)

    print("\n===== REAL CRIME DATA: JALANDHAR =====")
    print(report.to_string(index=False))

    print("\nTotal crimes against women in the latest available field:")
    print(row.get("totcrwom24"))

    # Save a clean report for our website
    report.to_csv(
        "data/jalandhar_crime_summary.csv",
        index=False
    )

    print("\nReport saved to data/jalandhar_crime_summary.csv")