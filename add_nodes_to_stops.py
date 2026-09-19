# this script matches the stops to nearest osm node 
# was developed in explore_osm.py
import osmnx as ox
import pandas as pd
import os

DATA_DIR = "data"
GTFS_DIR = os.path.join(DATA_DIR, "kitsap_gtfs")
OSM_DIR = os.path.join(DATA_DIR, "kitsap_osm")

def get_graph():
    graph = ox.load_graphml(os.path.join(OSM_DIR, "network.graphml"))
    return graph

def get_stops():
    stops_df = pd.read_csv(os.path.join(GTFS_DIR,"stops.txt"))
    return stops_df

def add_nodes_to_stops():
    stops_df = get_stops()
    graph = get_graph()
    stop_lons = stops_df['stop_lon'].tolist()
    stop_lats = stops_df['stop_lat'].tolist()
    nearest_node_ids = ox.nearest_nodes(graph, X=stop_lons, Y=stop_lats)

    # add it to the stops
    stops_df['osmnx_node_id'] = nearest_node_ids
    # see if got first few
    print(stops_df[['stop_id', 'stop_name', 'osmnx_node_id']].head())
    stops_df.to_csv(os.path.join(DATA_DIR, "tmp",'stops_w_nearest_nodes.csv'), index=False)

if __name__ == "__main__":
    add_nodes_to_stops()
