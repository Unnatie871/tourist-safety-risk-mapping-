
import pandas as pd

# Load the real NCRB dataset
df = pd.read_csv("data/ncrb_crime_data_2022.csv")

# Select Jalandhar
jalandhar = df[
    df["dis"].astype(str).str.contains(
        "Jalandhar", case=False, na=False
    )
]

if jalandhar.empty:
    print("Jalandhar was not found.")
else:
    row = jalandhar.iloc[0]

    print("\n===== JALANDHAR CRIME STATISTICS =====")
    print("District:", row["dis"])
    print("State:", row["state"])

    # Display selected statistics for each available year
    columns = [
        ("Reported rape cases", "totrape"),
        ("Reported murder cases", "mdrrape"),
        ("Cruelty-related cases", "crlhus"),
        ("Dowry deaths", "dwydeath"),
        ("Acid attacks", "acidatt"),
        ("Kidnapping/abduction cases", "totkidabd"),
        ("Crimes against women (IPC/BNS)", "totcrwom"),
    ]

    for year in ["22", "23", "24"]:
        print(f"\n--- Year ending in {year} ---")

        for label, prefix in columns:
            column = prefix + year

            if column in df.columns:
                value = row[column]

                if pd.notna(value):
                    print(f"{label}: {value}")

    print("\nSource: Downloaded NCRB district-level dataset")
    print("Note: These are district-level reported statistics.")
