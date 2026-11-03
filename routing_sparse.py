import numpy as np
import pandas as pd
import folium
import uuid

from pathlib import Path
from scipy.sparse import load_npz
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree


# Global variables
A = None
NODE_IDS = None
NODE_COORDINATES = None
FACILITIES = None
NODE_TREE = None


def prepare_routing():

    global A, NODE_IDS, NODE_COORDINATES
    global FACILITIES, NODE_TREE

    if A is None:

        print("Loading sparse road network...")

        A = load_npz("data/jalandhar_roads_sparse.npz")

        NODE_IDS = np.load(
            "data/jalandhar_node_ids.npy"
        )

        NODE_COORDINATES = np.load(
            "data/jalandhar_node_coordinates.npy"
        )

        NODE_TREE = cKDTree(NODE_COORDINATES)

        print("Sparse road network loaded!")

    if FACILITIES is None:

        print("Loading emergency facilities...")

        df = pd.read_csv(
            "data/jalandhar_sparse_facilities.csv"
        )

        FACILITIES = df.to_dict("records")

        print("Emergency facilities loaded!")


def generate_route(start_lat, start_lon):

    prepare_routing()

    # Find the nearest road node to the tourist
    _, start_index = NODE_TREE.query(
        [start_lon, start_lat]
    )

    start_index = int(start_index)

    print("Finding nearest reachable emergency facility...")

    # Calculate shortest distances from the starting node
    distances, predecessors = dijkstra(
        A,
        directed=True,
        indices=start_index,
        return_predecessors=True
    )

    nearest_facility = None
    shortest_distance = float("inf")

    # Find the nearest reachable emergency facility
    for facility in FACILITIES:

        facility_index = int(facility["node_index"])

        distance = distances[facility_index]

        if distance < shortest_distance:

            shortest_distance = distance
            nearest_facility = facility

    if nearest_facility is None or not np.isfinite(shortest_distance):

        raise ValueError(
            "No reachable emergency facility found."
        )

    destination_index = int(
        nearest_facility["node_index"]
    )

    # Reconstruct the shortest route
    route = []

    current = destination_index

    while current != start_index and current != -9999:

        route.append(current)

        current = int(predecessors[current])

    if current != start_index:

        raise ValueError("Route reconstruction failed.")

    route.append(start_index)

    route.reverse()

    # Convert node indices into geographic coordinates
    # Convert road node indices into geographic coordinates
    route_coordinates = [
    [
        NODE_COORDINATES[index][1],
        NODE_COORDINATES[index][0]
    ]
    for index in route
]

# Add the tourist's exact GPS location at the beginning
    route_coordinates.insert(
    0,
    [start_lat, start_lon]
)

# Add the exact emergency facility location at the end
    route_coordinates.append(
    [
        nearest_facility["latitude"],
        nearest_facility["longitude"]
    ]
) 

    # Create the route map
    route_map = folium.Map(
        location=[start_lat, start_lon],
        zoom_start=13
    )

    # Mark tourist location
    folium.Marker(
        [start_lat, start_lon],
        popup="Your Current Location",
        tooltip="Starting Point",
        icon=folium.Icon(color="blue", icon="user")
    ).add_to(route_map)

    # Mark emergency facility
    folium.Marker(
        [
            nearest_facility["latitude"],
            nearest_facility["longitude"]
        ],
        popup=nearest_facility.get("name", "Emergency Facility"),
        tooltip="Nearest Emergency Facility",
        icon=folium.Icon(color="red", icon="plus-sign")
    ).add_to(route_map)

    # Draw the route
    folium.PolyLine(
        route_coordinates,
        color="blue",
        weight=5,
        opacity=0.8,
        tooltip="Shortest Road Route"
    ).add_to(route_map)

    # Fit map to route
    route_map.fit_bounds(route_coordinates)

    # Save map
    Path("static/routes").mkdir(
        parents=True,
        exist_ok=True
    )

    map_filename = f"route_{uuid.uuid4().hex}.html"

    route_map.save(
        f"static/routes/{map_filename}"
    )

    return {
        "facility_name": nearest_facility.get(
            "name", "Emergency Facility"
        ),
        "facility_type": nearest_facility["type"],
        "distance_metres": shortest_distance,
        "map_filename": map_filename
    } 