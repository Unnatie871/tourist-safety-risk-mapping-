import osmnx as ox
from pathlib import Path

# Create the data folder if it does not exist
data_folder = Path("data")
data_folder.mkdir(exist_ok=True)

# Location where the road network will be saved
graph_file = data_folder / "jalandhar_drive.graphml"

print("Preparing Jalandhar road network...")

if graph_file.exists():
    print("Road network already exists!")
    print("File:", graph_file)
else:
    print("Downloading road network from OpenStreetMap...")
    print("This may take a few minutes. Please wait.")

    graph = ox.graph_from_place(
        "Jalandhar, Punjab, India",
        network_type="drive"
    )

    print("Download completed!")
    print("Saving road network locally...")

    ox.io.save_graphml(graph, filepath=graph_file)

    print("Road network saved successfully!")
    print("File:", graph_file)
    print("Nodes:", len(graph.nodes))
    print("Road segments:", len(graph.edges))  