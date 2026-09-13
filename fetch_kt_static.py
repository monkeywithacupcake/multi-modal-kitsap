import os
import requests
import zipfile
import pandas as pd

# plan to put zip into a data folder
DATA_DIR = "./data/kitsap_gtfs"
#STATIC_ZIP_URL = "https://kitsaptransit.com"
#STATIC_ZIP_URL = "https://transit.land"
#STATIC_ZIP_URL = "https://data.trilliumtransit.com/gtfs/kitsapcounty-wa-us/kitsapcounty-wa-us--flex-v2.zip"
#ZIP_FILE_PATH = os.path.join(DATA_DIR, "kitsap_transit_static.zip")
STATIC_ZIP_URL = "https://gtfs.sound.obaweb.org/prod/20_gtfs.zip"
ZIP_FILE_PATH = os.path.join(DATA_DIR, "20_gtfs.zip")

os.makedirs(DATA_DIR, exist_ok=True)

def download_static_gtfs():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(STATIC_ZIP_URL, headers=headers, stream=True)
    if response.status_code == 200:
        with open(ZIP_FILE_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("YAY Download complete.")
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

def extract_gtfs():
    with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)

def profile_network_density():
    # Load foundational static files into dataframes
    stops_df = pd.read_csv(os.path.join(DATA_DIR, "stops.txt"))
    routes_df = pd.read_csv(os.path.join(DATA_DIR, "routes.txt"))
    trips_df = pd.read_csv(os.path.join(DATA_DIR, "trips.txt"))
    
    print(f"count stops or nodes: {len(stops_df)}")
    print(f"count of routes: {len(routes_df)}")
    print(f"count of trips: {len(trips_df)}")
    
    # sep ferries Type 4 = Ferry infrastructure in GTFS spec
    ferries = routes_df[routes_df['route_type'] == 4]
    print(f"Ferry Routes: {len(ferries)}")
    for idx, row in ferries.iterrows():
        # look at terminal make sure tehse are ferries
        print(f"   - Route [{row['route_short_name']}]: {row['route_long_name']}")

if __name__ == "__main__":
    download_static_gtfs()
    extract_gtfs()
    profile_network_density()
