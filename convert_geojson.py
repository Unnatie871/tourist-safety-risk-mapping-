import json
import csv

# Step 1: Open the GeoJSON file
with open("data/export.geojson", "r", encoding="utf-8") as file:
    data = json.load(file)

# Step 2: Create a list to store the locations
locations = []

# Step 3: Read each location from the file
for feature in data.get("features", []):

    properties = feature.get("properties") or {}
    geometry = feature.get("geometry") or {}

    # Get the location name
    name = properties.get("name", "Name unavailable")

    # Get the type of location
    amenity = properties.get("amenity", "Unknown")

    # Get latitude and longitude
    coordinates = geometry.get("coordinates")

    if geometry.get("type") == "Point" and coordinates:
        longitude = coordinates[0]
        latitude = coordinates[1]

    else:
        # For non-point features, calculate an approximate center
        points = []

        def collect_points(value):
            if not isinstance(value, list):
                return

            if (
                len(value) >= 2
                and isinstance(value[0], (int, float))
                and isinstance(value[1], (int, float))
            ):
                points.append((value[0], value[1]))
            else:
                for item in value:
                    collect_points(item)

        collect_points(coordinates)

        if not points:
            continue

        longitude = sum(point[0] for point in points) / len(points)
        latitude = sum(point[1] for point in points) / len(points)

    # Store the location details
    locations.append({
        "name": name,
        "type": amenity,
        "latitude": latitude,
        "longitude": longitude,
        "source": "OpenStreetMap"
    })

# Step 4: Save the locations as a CSV file
output_file = "data/jalandhar_emergency_points.csv"

with open(output_file, "w", newline="", encoding="utf-8") as file:
    fieldnames = ["name", "type", "latitude", "longitude", "source"]

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(locations)

# Step 5: Display the result
print("Conversion completed!")
print("Total locations:", len(locations))
print("Saved to:", output_file) 