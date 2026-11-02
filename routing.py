import osmnx as ox
import networkx as nx
import pandas as pd
import folium
import uuid

from pathlib import Path

# Cache the road network and help facilities
G = None
HELP_FACILITIES = None


def prepare_routing():
    """Load and prepare routing data before a tourist requests a route."""
    global G, HELP_FACILITIES

    # Load the road network only once
    if G is None:
        graph_file = Path("data/jalandhar_drive.graphml")

        if not graph_file.exists():
            raise FileNotFoundError(
                "Saved road network not found. "
                "Run prepare_road_network.py first."
            )

        print("Loading saved road network...")
        G = ox.io.load_graphml(graph_file)
        print("Road network loaded!")

    # Prepare help facilities only once
    if HELP_FACILITIES is None:
        print("Preparing help facilities...")

        df = pd.read_csv("data/jalandhar_emergency_points.csv")

        df = df[
            df["type"].isin(["hospital", "police"])
        ].dropna(
            subset=["latitude", "longitude"]
        ).copy()

        # Find the road-network node for every facility
        nodes = ox.distance.nearest_nodes(
            G,
            X=df["longitude"].to_numpy(),
            Y=df["latitude"].to_numpy()
        )

        df["road_node"] = nodes

        HELP_FACILITIES = df.to_dict("records")

        print("Help facilities prepared!")


def generate_route(start_lat, start_lon):
    # Ensure routing data is ready
    prepare_routing()

    # Find the nearest road node to the tourist
    start_node = ox.distance.nearest_nodes(
        G,
        X=start_lon,
        Y=start_lat
    )

    print("Finding the nearest reachable help facility...")

    # Calculate road distances once
    distances = nx.single_source_dijkstra_path_length(
        G,
        start_node,
        weight="length"
    )

    nearest_help = None
    nearest_help_node = None
    shortest_distance = float("inf")

    # Select the closest reachable facility by road
    for facility in HELP_FACILITIES:
        help_node = facility["road_node"]

        if help_node in distances:
            distance = distances[help_node]

            if distance < shortest_distance:
                shortest_distance = distance
                nearest_help = facility
                nearest_help_node = help_node

    if nearest_help is None:
        raise ValueError("No reachable help facility was found.")

    # Calculate the route using A*
    route = nx.astar_path(
        G,
        start_node,
        nearest_help_node,
        heuristic=lambda u, v: ox.distance.great_circle(
            G.nodes[u]["y"],
            G.nodes[u]["x"],
            G.nodes[v]["y"],
            G.nodes[v]["x"]
        ),
        weight="length"
    )

    # Create the map
    # Calculate the map bounds using the complete route
    route_map = folium.Map(
    location=[start_lat, start_lon],
    zoom_start=12
) 

    # Mark the tourist's current location
        # Mark the tourist's current location
    folium.Marker(
        [start_lat, start_lon],
        popup="<b>START</b><br>Your Current Location",
        tooltip="START: Your Current Location",
        icon=folium.Icon(
            color="green",
            icon="play",
            prefix="fa"
        )
    ).add_to(route_map) 

    # Mark the selected help facility
        # Mark the selected help facility
    folium.Marker(
        [
            nearest_help["latitude"],
            nearest_help["longitude"]
        ],
        popup=(
            f"<b>DESTINATION</b><br>"
            f"<b>Facility:</b> {nearest_help['name']}<br>"
            f"<b>Type:</b> {nearest_help['type']}<br>"
            f"<b>Road Distance:</b> "
            f"{round(shortest_distance)} metres"
        ),
        tooltip=f"DESTINATION: {nearest_help['name']}",
        icon=folium.Icon(
            color="red",
            icon="plus",
            prefix="fa"
        )
    ).add_to(route_map) 

    # Get route coordinates
        # Get route coordinates that follow the actual road geometry
        # Build route coordinates using the actual road geometry
    route_coordinates = []

    # Always begin at the user's exact current location
    route_coordinates.append((start_lat, start_lon))

    for u, v in zip(route[:-1], route[1:]):
        edge_data = G.get_edge_data(u, v)

        if not edge_data:
            continue

        # Select the shortest road segment between these nodes
        edge = min(
            edge_data.values(),
            key=lambda data: data.get("length", float("inf"))
        )

        if edge.get("geometry") is not None:
            road_points = [
                (lat, lon)
                for lon, lat in edge["geometry"].coords
            ]

            # Keep the geometry in the correct direction
            if road_points:
                node_start = (
                    G.nodes[u]["y"],
                    G.nodes[u]["x"]
                )

                first_distance = (
                    abs(road_points[0][0] - node_start[0])
                    + abs(road_points[0][1] - node_start[1])
                )

                last_distance = (
                    abs(road_points[-1][0] - node_start[0])
                    + abs(road_points[-1][1] - node_start[1])
                )

                if last_distance < first_distance:
                    road_points.reverse()

                route_coordinates.extend(road_points)

        # Include the next road node
        route_coordinates.append(
            (G.nodes[v]["y"], G.nodes[v]["x"])
        )

    # Finish at the destination facility
    route_coordinates.append((
        float(nearest_help["latitude"]),
        float(nearest_help["longitude"])
    )) 

    # Add the final destination road node
    last_node = route[-1]
    route_coordinates.append(
        (G.nodes[last_node]["y"], G.nodes[last_node]["x"])
    ) 

    # Draw the route
        # Draw a dark outline underneath the route for better visibility
    folium.PolyLine(
        route_coordinates,
        color="#123047",
        weight=11,
        opacity=0.9
    ).add_to(route_map)

    # Draw the bright green A* route
    folium.PolyLine(
        route_coordinates,
        color="#00C853",
        weight=7,
        opacity=1.0,
        tooltip="A* Safe Route"
    ).add_to(route_map) 
        # Add a legend to explain the route map
    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        width: 210px;
        background-color: white;
        border: 2px solid #123047;
        z-index: 9999;
        padding: 12px;
        border-radius: 10px;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    ">
        <h4 style="margin-top: 0; margin-bottom: 10px;">
            Route Legend
        </h4>

        <div style="margin-bottom: 8px;">
            <span style="color: #00C853; font-size: 20px;">━━</span>
            A* Calculated Route
        </div>

        <div style="margin-bottom: 8px;">
            <span style="color: green;">●</span>
            Starting Location
        </div>

        <div>
            <span style="color: red;">●</span>
            Help Facility
        </div>
    </div>
    """

    route_map.get_root().html.add_child(
        folium.Element(legend_html)
    ) 
    # Automatically display the complete route
    route_map.fit_bounds(route_coordinates)

    # Give this request its own map file
    routes_folder = Path("static/routes")
    routes_folder.mkdir(parents=True, exist_ok=True)

    map_filename = f"routes/route_{uuid.uuid4().hex}.html"

    route_map.save(Path("static") / map_filename)

    print("Route map saved successfully!")

    return {
        "facility_name": str(nearest_help["name"]),
        "facility_type": str(nearest_help["type"]),
        "distance_metres": round(shortest_distance),
        "map_filename": map_filename
    }


if __name__ == "__main__":
    prepare_routing()

    result = generate_route(31.3260, 75.5762)

    print("Nearest help facility:", result["facility_name"])
    print("Facility type:", result["facility_type"])
    print("Road distance:", result["distance_metres"], "metres") 