import requests
import pandas as pd
import os

print("Connecting to the crime data source...")

url = (
    "https://livingatlas.esri.in/server1/rest/services/"
    "NCRB/District_Wise_Crime_Against_Women_2022/"
    "MapServer/0/query"
)

params = {
    "where": "1=1",
    "outFields": "*",
    "returnGeometry": "false",
    "f": "json"
}

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    result = response.json()

    if "error" in result:
        print("Server error:", result["error"])
    else:
        records = result.get("features", [])

        if not records:
            print("No records returned by the server.")
        else:
            df = pd.DataFrame(
                [record["attributes"] for record in records]
            )

            os.makedirs("data", exist_ok=True)

            output_file = "data/ncrb_crime_data_2022.csv"
            df.to_csv(output_file, index=False)

            print("\nSUCCESS! Crime data downloaded.")
            print("Total records:", len(df))
            print("Columns:", list(df.columns))
            print("Saved to:", output_file)
            print("\nFirst five records:")
            print(df.head())

except Exception as e:
    print("\nDownload failed:", e)
    print("We will try another approach if needed.") 