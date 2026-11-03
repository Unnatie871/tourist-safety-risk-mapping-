import osmnx as ox

# Load the original road network
print("Loading original road network...")

G = ox.io.load_graphml("data/jalandhar_drive.graphml")

print("Original graph loaded!")
# Remove unnecessary node attributes
for node, data in G.nodes(data=True):
    data.pop("street_count", None) 

# Remove unnecessary edge attributes
attributes_to_remove = [
    "osmid",
    "highway",
    "maxspeed",
    "name",
    "ref",
    "geometry"
]

for u, v, key, data in G.edges(keys=True, data=True):
    for attribute in attributes_to_remove:
        data.pop(attribute, None)

# Save the lightweight graph separately
output_file = "data/jalandhar_drive_light.graphml"

ox.io.save_graphml(G, output_file)

print("Lightweight graph created successfully!")
print("Saved at:", output_file)
print("Nodes:", len(G.nodes))
print("Edges:", len(G.edges)) 