import pandas as pd
import numpy as np

from scipy.spatial import cKDTree

print("Loading node coordinates...")

node_coordinates = np.load(
    "data/jalandhar_node_coordinates.npy"
)

node_ids = np.load(
    "data/jalandhar_node_ids.npy"
)

# Convert coordinates into a searchable spatial index
tree = cKDTree(node_coordinates)

print("Loading emergency facilities...")

df = pd.read_csv(
    "data/jalandhar_emergency_points.csv"
)

df = df[
    df["type"].isin(["hospital", "police"])
].dropna(
    subset=["latitude", "longitude"]
).copy()

# Find the nearest road-network node for each facility
facility_coordinates = df[
    ["longitude", "latitude"]
].to_numpy()

distances, indices = tree.query(
    facility_coordinates,
    k=1
)

df["node_index"] = indices

df["road_node"] = [
    node_ids[index]
    for index in indices
]

# Save the prepared facilities
df.to_csv(
    "data/jalandhar_sparse_facilities.csv",
    index=False
)

print("Emergency facilities prepared successfully!")
print("Total facilities:", len(df))
print("Hospitals:", (df["type"] == "hospital").sum())
print("Police stations:", (df["type"] == "police").sum())

print("\nFirst five prepared facilities:")
print(
    df[["type", "latitude", "longitude", "node_index"]].head()
) 