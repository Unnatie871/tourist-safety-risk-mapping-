import osmnx as ox
import numpy as np
from scipy.sparse import csr_matrix, save_npz

print("Loading lightweight road network...")

G = ox.io.load_graphml("data/jalandhar_drive_light.graphml")

print("Road network loaded!")

# Assign a numeric index to every node
nodes = list(G.nodes())

node_to_index = {
    node: index
    for index, node in enumerate(nodes)
}

print("Converting road connections...")

# Store the minimum distance for each directed node pair
edge_weights = {}

for u, v, data in G.edges(data=True):

    row = node_to_index[u]
    col = node_to_index[v]
    distance = float(data["length"])

    key = (row, col)

    if key not in edge_weights or distance < edge_weights[key]:
        edge_weights[key] = distance

rows = []
cols = []
weights = []

for (row, col), distance in edge_weights.items():
    rows.append(row)
    cols.append(col)
    weights.append(distance) 

# Create the sparse adjacency matrix
A = csr_matrix(
    (weights, (rows, cols)),
    shape=(len(nodes), len(nodes))
)

# Save the matrix
save_npz("data/jalandhar_roads_sparse.npz", A)

# Save node information separately
node_data = np.array(
    [
        [float(G.nodes[node]["x"]), float(G.nodes[node]["y"])]
        for node in nodes
    ],
    dtype=np.float64
)

np.save("data/jalandhar_node_coordinates.npy", node_data)

# Save the original node IDs in the same order
np.save("data/jalandhar_node_ids.npy", np.array(nodes))

print("Sparse graph created successfully!")
print("Total nodes:", len(nodes))
print("Total connections:", A.nnz)
print("Matrix shape:", A.shape)
print("Matrix size:", round(A.data.nbytes / 1024 / 1024, 2), "MB") 