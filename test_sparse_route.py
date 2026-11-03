import psutil
import os

from routing_sparse import generate_route

# Measure memory before routing
process = psutil.Process(os.getpid())

print(
    "Memory before routing:",
    round(process.memory_info().rss / 1024 / 1024, 2),
    "MB"
)

# Test location in Jalandhar
start_lat = 31.3260
start_lon = 75.5762

print("\nGenerating emergency route...")

result = generate_route(start_lat, start_lon)

print("\nROUTE GENERATED SUCCESSFULLY!")

print("Nearest facility:", result["facility_name"])
print("Facility type:", result["facility_type"])

print(
    "Road distance:",
    round(result["distance_metres"] / 1000, 2),
    "km"
)

print("Map file:", result["map_filename"])

# Measure memory after routing
print(
    "\nMemory after routing:",
    round(process.memory_info().rss / 1024 / 1024, 2),
    "MB"
) 