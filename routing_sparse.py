import numpy as np
import pandas as pd
import folium
import uuid
import heapq

from pathlib import Path
from scipy.sparse import load_npz
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

        A = load_npz(
            "data/jalandhar_roads_sparse.npz"
        ).tocsr()

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


# Calculate straight-line distance using Haversine formula
def haversine_distance(point, goals):

    lon1 = np.radians(point[0])
    lat1 = np.radians(point[1])

    lon2 = np.radians(goals[:, 0])
    lat2 = np.radians(goals[:, 1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    a = np.clip(a, 0, 1)

    distance = (
        2
        * 6371000
        * np.arcsin(np.sqrt(a))
    )

    return np.min(distance)


# A* Search Algorithm
def astar_search(start_index, goal_indices):

    goal_indices = np.unique(goal_indices)

    goal_coordinates = NODE_COORDINATES[goal_indices]

    number_of_nodes = A.shape[0]

    # Store the actual distance from the start
    g_score = np.full(
        number_of_nodes,
        np.inf
    )

    # Store the previous node for route reconstruction
    came_from = np.full(
        number_of_nodes,
        -1,
        dtype=int
    )

    # Priority queue stores (f_score, g_score, node)
    open_set = []

    g_score[start_index] = 0

    start_heuristic = haversine_distance(
        NODE_COORDINATES[start_index],
        goal_coordinates
    )

    heapq.heappush(
        open_set,
        (
            start_heuristic,
            0,
            start_index
        )
    )

    print("Running A* Search...")

    while open_set:

        f_current, current_g, current = heapq.heappop(
            open_set
        )

        # Ignore outdated queue entries
        if current_g > g_score[current]:
            continue

        # Stop when the nearest reachable goal is reached
        if current in goal_indices:

            print("Emergency facility reached using A*!")

            return current, came_from, current_g

        # Get all road connections of the current node
        start_position = A.indptr[current]
        end_position = A.indptr[current + 1]

        neighbors = A.indices[
            start_position:end_position
        ]

        weights = A.data[
            start_position:end_position
        ]

        # Explore neighbouring road nodes
        for neighbor, weight in zip(neighbors, weights):

            tentative_g = current_g + weight

            if tentative_g < g_score[neighbor]:

                came_from[neighbor] = current

                g_score[neighbor] = tentative_g

                h_score = haversine_distance(
                    NODE_COORDINATES[neighbor],
                    goal_coordinates
                )

                f_score = tentative_g + h_score

                heapq.heappush(
                    open_set,
                    (
                        f_score,
                        tentative_g,
                        neighbor
                    )
                )

    raise ValueError(
        "No reachable emergency facility found."
    )


def generate_route(start_lat, start_lon):

    prepare_routing()

    # Find the nearest road node to the tourist
    _, start_index = NODE_TREE.query(
        [start_lon, start_lat]
    )

    start_index = int(start_index)

    print("Finding nearest reachable emergency facility...")

    # Get all emergency facility road nodes
    goal_indices = [
        int(facility["node_index"])
        for facility in FACILITIES
    ]

    # Run A* Search
    destination_index, came_from, shortest_distance = astar_search(
        start_index,
        goal_indices
    )

    # Find the facility at the destination node
    nearest_facility = next(
        facility
        for facility in FACILITIES
        if int(facility["node_index"]) == destination_index
    )

    # Reconstruct the shortest route
    route = []

    current = destination_index

    while current != start_index:

        route.append(current)

        current = int(came_from[current])

        if current == -1:

            raise ValueError(
                "Route reconstruction failed."
            )

    route.append(start_index)

    route.reverse()

    # Convert road node indices into geographic coordinates
    route_coordinates = [
        [
            NODE_COORDINATES[index][1],
            NODE_COORDINATES[index][0]
        ]
        for index in route
    ]

    # Add the tourist's exact GPS location
    route_coordinates.insert(
        0,
        [start_lat, start_lon]
    )

    # Add the exact emergency facility location
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
        icon=folium.Icon(
            color="blue",
            icon="user"
        )
    ).add_to(route_map)

    # Mark emergency facility
    folium.Marker(
        [
            nearest_facility["latitude"],
            nearest_facility["longitude"]
        ],
        popup=nearest_facility.get(
            "name",
            "Emergency Facility"
        ),
        tooltip="Nearest Emergency Facility",
        icon=folium.Icon(
            color="red",
            icon="plus-sign"
        )
    ).add_to(route_map)

    # Draw the route
    folium.PolyLine(
        route_coordinates,
        color="blue",
        weight=5,
        opacity=0.8,
        tooltip="A* Shortest Road Route"
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
            "name",
            "Emergency Facility"
        ),
        "facility_type": nearest_facility["type"],
        "distance_metres": shortest_distance,
        "map_filename": map_filename
    } 