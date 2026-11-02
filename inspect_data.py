import pandas as pd

# Load the Jalandhar dataset
df = pd.read_csv("data/jalandhar_help_points.csv")

# Display the dataset size
print("Total rows:", len(df))

# Display the column names
print("\nColumn names:")
print(df.columns.tolist())

# Count each type of mapped location
print("\nLocation types:")
print(df["type"].value_counts(dropna=False))

# Check missing values
print("\nMissing values:")
print(df.isnull().sum())

# Count unnamed locations
unnamed = (
    df["name"].isna()
    | df["name"].astype(str).str.strip().str.lower().isin(
        ["name unavailable", "", "nan"]
    )
)

print("\nLocations without a usable name:", unnamed.sum())

# Check duplicate coordinates
duplicates = df.duplicated(
    subset=["latitude", "longitude"]
).sum()

print("Duplicate coordinates:", duplicates)

# Check whether coordinates are within Jalandhar's approximate region
valid_coordinates = (
    df["latitude"].between(30.0, 32.0)
    & df["longitude"].between(74.0, 76.0)
)

print("Coordinates within broad Punjab bounds:", valid_coordinates.sum())

# Display a sample
print("\nFirst five records:")
print(df.head())  
print("\nChecking new emergency dataset...")

new_df = pd.read_csv("data/jalandhar_emergency_points.csv")

print("Total new locations:", len(new_df))

print("\nTypes of locations:")
print(new_df["type"].value_counts())

print("\nMissing values:")
print(new_df.isnull().sum())

print("\nFirst five locations:")
print(new_df.head()) 