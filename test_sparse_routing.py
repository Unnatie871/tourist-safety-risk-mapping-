import numpy as np
from scipy.sparse import load_npz
from scipy.sparse.csgraph import dijkstra

print("Loading sparse road network...")

A = load_npz("data/jalandhar_roads_sparse.npz")
node_ids = np.load("data/jalandhar_node_ids.npy")

print("Sparse graph loaded!")

# Select two nodes for testing
start_index = 0
destination_index = 1000

print("Starting shortest-path calculation...")

distances, predecessors = dijkstra(
    A,
    directed=True,
    indices=start_index,
    return_predecessors=True
)

distance = distances[destination_index]

if np.isinf(distance):
    print("No route found between these nodes.")
else:
    print("Route found!")
    print("Starting node:", node_ids[start_index])
    print("Destination node:", node_ids[destination_index])
    print("Shortest road distance:", round(distance, 2), "metres")

    # Reconstruct the route
    route = []
    current = destination_index

    while current != start_index and current != -9999:
        route.append(current)
        current = predecessors[current]

    if current == start_index:
        route.append(start_index)
        route.reverse()

        print("Total nodes in route:", len(route))
        print("First 5 route nodes:", route[:5])
    else:
        print("Could not reconstruct route.") 