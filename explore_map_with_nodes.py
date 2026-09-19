# explore_map with nodes
import osmnx as ox
import pandas as pd
import pydeck as pdk
import os

DATA_DIR = "data"

DATA_DIR = "data"
GTFS_DIR = os.path.join(DATA_DIR, "kitsap_gtfs")
OSM_DIR = os.path.join(DATA_DIR, "kitsap_osm")

graph = ox.load_graphml(os.path.join(OSM_DIR, "network.graphml"))
# split
nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)
# Clean up multi-input tags for easier filtering/visual mapping
edges_gdf['highway'] = edges_gdf['highway'].astype(str)

# load the stops with nodes and routes
stops_df = pd.read_csv(os.path.join(DATA_DIR, "tmp", "stops_w_routes_nearest_nodes.csv"))


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

# color nodes that are next to stops
def set_node_color(row):
    if 'osm' in str(stops_df['osmnx_node_id']):
        return [255, 165, 0, 200]  #  ORANGE for next to STOP
    else:
        return [100, 100, 100, 150] # Gray for  not next to stop

nodes_gdf['node_color'] = nodes_gdf.apply(set_node_color, axis=1)

# get osmid as a regular column and then filter if it is one used in stops
nodes_gdf = nodes_gdf.reset_index() 
filtered_nodes = nodes_gdf[nodes_gdf["osmid"].isin(stops_df['osmnx_node_id'])]



node_layer = pdk.Layer(
    "ScatterplotLayer",
    #nodes_gdf,
    filtered_nodes,
    get_position="[x, y]",
    get_color="[255, 165, 0, 200]", #"node_color", 
    get_radius=100, # making bigger so i can see
    pickable=False,
    opacity=0.6
    
)

# put stops as points
stop_layer = pdk.Layer(
    "ScatterplotLayer",
    stops_df,
    get_position="[stop_lon, stop_lat]",
    get_color="[0, 100, 255, 200]", # Blue points
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
    #layers=[street_layer, node_layer, stop_layer],
    layers=[node_layer, stop_layer],
    initial_view_state=view_state#,
    #tooltip={"text": "Stop:{stop_name}, Routes:{route_count}-{route_names}"} # only works for pickable layer
)

# save to explore
r.to_html("node_explorer.html")
