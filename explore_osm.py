import osmnx as ox
import pandas as pd
import os

DATA_DIR = "data"
GTFS_DIR = os.path.join(DATA_DIR, "kitsap_gtfs")
OSM_DIR = os.path.join(DATA_DIR, "kitsap_osm")

graph = ox.load_graphml(os.path.join(OSM_DIR, "network.graphml"))

# split
nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)
# how much am i looking at
print("--- NODE ATTRIBUTES ---")
print(nodes_gdf.columns)
print(nodes_gdf[['x', 'y']].head()) # 'x' is longitude, 'y' is latitude

print("\n--- EDGE ATTRIBUTES ---")
print(edges_gdf.columns)
print(edges_gdf.head())

# can match to stops?
# Load your GTFS stops file
stops_df = pd.read_csv(os.path.join(GTFS_DIR,"stops.txt"))
print(stops_df[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']].head())
routes = pd.read_csv(os.path.join(GTFS_DIR,"routes.txt"))
trips = pd.read_csv(os.path.join(GTFS_DIR,"trips.txt"))
stop_times = pd.read_csv(os.path.join(GTFS_DIR,'stop_times.txt'))
stop_route_mapping = stop_times.merge(trips, on='trip_id')[['stop_id', 'route_id']]
# ugh save and look
stop_route_mapping.to_csv(os.path.join(DATA_DIR, "tmp",'stop_route_mapping.csv'), index=False)
stop_route_mapping = stop_times.merge(trips, on='trip_id')[['stop_id', 'route_id']].drop_duplicates()
print(stop_route_mapping[['stop_id','route_id']].head())
stop_routes = (
    stop_route_mapping.groupby("stop_id")
    .agg(
        route_count=("route_id", "count"),
        route_names=(
            "route_id",
            lambda x: ", ".join(x.dropna().unique()))
    )
    .reset_index()
)
print(stop_routes.head())
stops_df = pd.merge(stops_df, stop_routes, on="stop_id", how="left")

# try match with lat lon
stop_lons = stops_df['stop_lon'].tolist()
stop_lats = stops_df['stop_lat'].tolist()

# try to match nearest nodes
# X = longitudes, Y = latitudes
# nearest_nodes depends on scikit-learn if don't project first
nearest_node_ids = ox.nearest_nodes(graph, X=stop_lons, Y=stop_lats)
stops_df['osmnx_node_id'] = nearest_node_ids

# see if got first few
print(stops_df[['stop_id', 'stop_name', 'route_count', 'osmnx_node_id']].head())

# save and look
stops_df.to_csv(os.path.join(DATA_DIR, "tmp",'stops_w_routes_nearest_nodes.csv'), index=False)

