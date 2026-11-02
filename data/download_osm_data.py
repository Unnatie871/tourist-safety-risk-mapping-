import requests
import pandas as pd
import time
from datetime import datetime, timezone

# STEP 1: Find Jalandhar
print("Finding Jalandhar...")

geocoding_url = "https://nominatim.openstreetmap.org/search"

params = {
    "city": "Jalandhar",
    "state": "Punjab",
    "country": "India",
    "format": "json",
    "limit": 1
}

headers = {
    "User-Agent": "TouristSafetyStudentProject/1.0 (educational project)"
}

response = requests.get(
    geocoding_url,
    params=params,
    headers=headers,
    timeout=30
)

response.raise_for_status()
locations = response.json()

if not locations:
    raise Exception("Could not find Jalandhar.")

bounds = locations[0]["boundingbox"]

south = float(bounds[0])
north = float(bounds[1])
west = float(bounds[2])
east = float(bounds[3])

print("Jalandhar found!")


# STEP 2: Query real mapped safety features
print("Requesting OpenStreetMap data...")

query = f"""
[out:json][timeout:180];

(
  nwr["amenity"~"^(police|hospital|fire_station|clinic|pharmacy)$"]
     ({south},{west},{north},{east});

  node["highway"="street_lamp"]
     ({south},{west},{north},{east});

  nwr["man_made"="surveillance"]
     ({south},{west},{north},{east});

  nwr["surveillance"="camera"]
     ({south},{west},{north},{east});
);

out center tags;
"""

endpoints = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

elements = None

for endpoint in endpoints:
    try:
        print("Trying OpenStreetMap query server...")

        response = requests.post(
            endpoint,
            data={"data": query},
            headers=headers,
            timeout=200
        )

        response.raise_for_status()
        elements = response.json()["elements"]

        print("Data downloaded successfully!")
        break

    except Exception as error:
        print("This server did not work:", error)
        time.sleep(3)

if elements is None:
    raise Exception(
        "Could not download data. Please retry after a few minutes."
    )


# STEP 3: Organise the real records
records = []

for element in elements:
    tags = element.get("tags", {})

    if "lat" in element and "lon" in element:
        latitude = element["lat"]
        longitude = element["lon"]

    elif "center" in element:
        latitude = element["center"]["lat"]
        longitude = element["center"]["lon"]

    else:
        continue

    feature_type = (
        tags.get("amenity")
        or tags.get("highway")
        or tags.get("man_made")
        or tags.get("surveillance")
        or "other"
    )

    records.append({
        "name": tags.get("name", "Name unavailable"),
        "type": feature_type,
        "latitude": latitude,
        "longitude": longitude,
        "osm_element_type": element.get("type"),
        "osm_id": element.get("id"),
        "source": "OpenStreetMap",
        "retrieved_utc": datetime.now(timezone.utc).isoformat()
    })


# STEP 4: Remove duplicate OSM elements
df = pd.DataFrame(records)

if df.empty:
    raise Exception(
        "No mapped features were returned. Try again later."
    )

df = df.drop_duplicates(
    subset=["osm_element_type", "osm_id"]
)


# STEP 5: Save without overwriting existing files
output_file = "data/jalandhar_safety_features.csv"

df.to_csv(output_file, index=False)

print("\nDATA COLLECTION COMPLETE!")
print("Total mapped features:", len(df))
print("\nFeature counts:")
print(df["type"].value_counts())
print("\nSaved to:", output_file)
print("\nFirst five records:")
print(df.head()) 