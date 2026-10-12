# here i want to take a subset of the graph
# and try to implement a version of dijkstra's algorithm
# AFAICT, this will not work with transit time tables, but good 
# for figuring out walk and bike part 
import os
import osmnx as ox
import networkx as nx
import osmnx as ox
import heapq
import matplotlib.pyplot as plt

DATA_DIR = "data"
OSM_DIR = os.path.join(DATA_DIR, "kitsap_osm")

# Pull a walkable street network around a point (lat, lon), 1.5 km radius
#G = ox.graph_from_point((47.55, -122.63), dist=1500, network_type="walk")
G = ox.load_graphml(os.path.join(OSM_DIR, "network.graphml"))

# Snap your start and end coordinates to the nearest graph nodes
# plaza 47.656393, -122.695569. old mill park 47.650535, -122.687566
orig_x = -122.695569
orig_y = 47.656393
dest_x = -122.687566
dest_y = 47.650535
orig = ox.distance.nearest_nodes(G, X=orig_x, Y=orig_y)
dest = ox.distance.nearest_nodes(G, X=dest_x, Y=dest_y)

# making some boundaries so my graph is visible while testing
margin = 0.01  # ~1 km in latitude; adjust as needed
north = max(orig_y, dest_y) + margin
south = min(orig_y, dest_y) - margin
east  = max(orig_x, dest_x) + margin
west  = min(orig_x, dest_x) - margin
G = ox.truncate.truncate_graph_bbox(G, bbox=(west, south, east, north))

# Shortest path by distance netowrkx uses (Dijkstra under the hood)
route = nx.shortest_path(G, orig, dest, weight="length")


# try to make my own start with length as weight just like netowrkx
def dijkstra_record(graph, source, target, weight="length"):
    dist = {source: 0.0}
    prev = {}
    heap = [(0.0, source)]
    visited = set()
    visit_order = []   # nodes in the order they were settled

    while heap:
        cost, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        visit_order.append(node)

        if node == target:
            break

        for neighbor, edge_map in graph[node].items():
            w = min(d.get(weight, float("inf")) for d in edge_map.values())
            new_cost = cost + w
            if new_cost < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_cost
                prev[neighbor] = node
                heapq.heappush(heap, (new_cost, neighbor))

    if target not in dist:
        return None, None, visit_order

    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    path.reverse()
    return path, dist[target], visit_order

def path_totals(graph, path):
    # Sum length (m) and travel time (s) along the path, using the cheapest parallel edge
    length_m, time_s = 0.0, 0.0
    for u, v in zip(path[:-1], path[1:]):
        edges = graph[u][v].values()
        best_len = min(d.get("length", float("inf")) for d in edges)
        best_time = min(d.get("travel_time", best_len / 1.4) for d in edges)
        length_m += best_len
        time_s += best_time
    return length_m, time_s


path, total_m, visited_nodes = dijkstra_record(G, orig, dest)
length_m, time_s = path_totals(G, path)
print(f"Distance: {length_m:.0f} m ({length_m/1000:.2f} km)")
print(f"Time at 1.4 m/s: {time_s/60:.1f} min")

# Plot the explored nodes in light gray, then the final route in red
fig, ax = ox.plot_graph(G, show=False, close=False, node_size=0,
                        edge_color="#cccccc", edge_linewidth=0.5)
xs = [G.nodes[n]["x"] for n in visited_nodes]
ys = [G.nodes[n]["y"] for n in visited_nodes]
ax.scatter(xs, ys, s=2, c="orange", zorder=3)





# Plot it
#ox.plot.plot_graph_route(Gbb, route)
ox.plot.plot_graph_route(G, path, ax=ax, route_color="red",
                    route_linewidth=4, show=False, close=False)
ax.set_title(f"{length_m/1000:.2f} km, {time_s/60:.1f} min")
plt.show()