# explore_map
import osmnx as ox
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import os
import numpy as np

DATA_DIR = "data"
GTFS_DIR = os.path.join(DATA_DIR, "kitsap_gtfs")
OSM_DIR = os.path.join(DATA_DIR, "kitsap_osm")

graph = ox.load_graphml(os.path.join(OSM_DIR, "network.graphml"))
# split
nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)
# Clean up multi-input tags for easier filtering/visual mapping
edges_gdf['highway'] = edges_gdf['highway'].astype(str)

print(edges_gdf.groupby('highway')['length'].agg(['mean', 'sum', 'count']))


# load the stops
stops_df = pd.read_csv(os.path.join(GTFS_DIR,"stops.txt"))


# 2. ASSIGN COLORS BY TAGS FOR VISUAL EXPLORATION
def assign_color(row):
    # Customize this logic based on the specific OSM tags you care about
    if 'cycleway' in str(row.get('bicycle', '')) or 'cycleway' in row['highway']:
        return [0, 200, 100, 200]  # Green for bikeways
    elif 'path' in row['highway'] or 'foot' in row['highway']:
        return [200, 10, 100, 200]   # purple for walk
    elif 'motorway' in row['highway'] or 'trunk' in row['highway']:
        return [255, 50, 50, 200]   # Red for major highways
    else:
        return [100, 100, 100, 150] # Gray for standard streets

edges_gdf['color'] = edges_gdf.apply(assign_color, axis=1)

# Pydeck requires a flat GeoDataFrame with geometry explicitly formatted
edges_gdf = edges_gdf.to_crs(epsg=4326)

# put streets on bottom layer (use tag for color)
street_layer = pdk.Layer(
    "GeoJsonLayer",
    edges_gdf,
    get_line_color="properties.color",
    get_line_width=4,
    pickable=False
)

# put stops as points
# stop_layer = pdk.Layer(
#     "ScatterplotLayer",
#     stops_df,
#     get_position="[stop_lon, stop_lat]",
#     get_color="[0, 100, 255, 200]", # Blue points
#     get_radius=30,
#     pickable=True
# )

# blargh, some of these stops are only worker driver stops
routes = pd.read_csv(os.path.join(GTFS_DIR,"routes.txt"))
# i think that some trip_ids are being read as str and some as int 
# sfixed in osm
trips = pd.read_csv(os.path.join(GTFS_DIR,"trips.txt"), dtype={'trip_id': str})
stop_times = pd.read_csv(os.path.join(GTFS_DIR,'stop_times.txt'), dtype={'trip_id': str})
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

# get route ids (should prob also do for commuters)
workers_route_ids = routes[
    routes['route_long_name'].str.contains('Worker/Driver', case=False, na=False) 
]['route_id']
# find only associated routes are in the workers_route_ids list
workers_only_stop_ids = stop_route_mapping.groupby('stop_id').filter(
    lambda x: x['route_id'].isin(workers_route_ids).all()
)['stop_id'].unique()
#wd_stops = stops_df[stops_df['stop_id'].isin(workers_only_stop_ids)]
#print(wd_stops[['stop_id', 'stop_name']])
#stops_df["color"] = np.where(stops_df["stop_id"].isin(workers_only_stop_ids), "orange", "blue")
# Define RGB arrays
ORANGE = [255, 165, 0]
BLUE = [0, 0, 255]

# have to use array instead of color name for pydeck
stops_df["stop_color"] = np.where(
    stops_df["stop_id"].isin(workers_only_stop_ids),
    pd.Series([ORANGE] * len(stops_df)),
    pd.Series([BLUE] * len(stops_df)),
)

# put stops as points
stop_layer = pdk.Layer(
    "ScatterplotLayer",
    stops_df,
    get_position="[stop_lon, stop_lat]",
    get_color="stop_color", #"[0, 100, 255, 200]", # Blue points
    get_radius=60, # making bigger so i can see
    pickable=True,
    opacity=0.6
)



# make interactive in pydeck - pydeck docks say use mean for good center
# view_state = pdk.ViewState(
#     latitude=nodes_gdf['y'].mean(),
#     longitude=nodes_gdf['x'].mean(),
#     zoom=13,
#     pitch=0
# )
#  use ck for now as explore
view_state = pdk.ViewState(
    latitude=47.6500,
    longitude=-122.7500,
    zoom=10.5,      # zoom to try not to see big area
    pitch=0,        # i keep forgetting that this is 2D v 45 for 3D
    bearing=0
)


r = pdk.Deck(
    layers=[street_layer, stop_layer],
    initial_view_state=view_state,
    tooltip={"text": "Stop:{stop_name}, Routes:{route_count}-{route_names}"} # only works for pickable layer
)

# save to explore
r.to_html("routing_explorer.html")
