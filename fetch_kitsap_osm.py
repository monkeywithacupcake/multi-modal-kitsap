import osmnx as ox
import os

# plan to put zip into a data folder
DATA_DIR = "./data/kitsap_osm"

place = "Kitsap County, Washington, USA"
aoi = ox.geocoder.geocode_to_gdf(place)

# fetch from osm
graph = ox.graph_from_place(place, network_type="all")

# save graphml - not sure if this is best
ox.save_graphml(graph, filepath=os.path.join(DATA_DIR, "network.graphml"))

# maybe .shp
#ox.save_graph_shapefile(graph, filepath=os.path.join(DATA_DIR, "./shapefiles/")

# split
#nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)

# Save edges to GeoJSON
#edges_gdf.to_file("edges.geojson", driver="GeoJSON")
#edges_gdf.drop(columns=["geometry"]).to_csv("edges.csv", index=True)
#nodes_gdf.drop(columns=["geometry"]).to_csv("node.csv", index=True)
