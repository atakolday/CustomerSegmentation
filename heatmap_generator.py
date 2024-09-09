import pandas as pd

from time import sleep
from tqdm import tqdm

from geopy.geocoders import Photon
from geopy.exc import GeocoderTimedOut

import folium
from folium.plugins import HeatMap

class HeatmapGenerator:
    def __init__(self):
        self.orders_cluster = pd.read_csv('data/Orders_Segmented.csv')
        self.customer_behavior = pd.read_csv('data/Customer_Behavior.csv')
        self.location_coordinates = {}

    def preprocess_data(self):
        # Extract customer IDs from Orders_Master
        customer_ids_orders = self.orders_cluster['CustomerID'].unique()

        # Filter Customer_Behavior data to include only customers from Orders_Master
        filtered_behavior_data = self.customer_behavior[self.customer_behavior['CustomerID'].isin(customer_ids_orders)]

        # Merge filtered behavior data with clusters for analysis (without modifying the main dataset)
        self.customer_with_behavior_and_clusters = filtered_behavior_data.merge(
            self.orders_cluster[['CustomerID', 'Cluster']], 
            on='CustomerID', how='inner'
        )

        # Add 'Location' column for API queries to Photon
        self.customer_with_behavior_and_clusters['Location'] = (
            self.customer_with_behavior_and_clusters['City'] + ', ' +
            self.customer_with_behavior_and_clusters['State'] + ', ' +
            self.customer_with_behavior_and_clusters['Country']
        )

        # Creates a dataframe with Cluster value as index, and each unique location as the column label, with values as count
        self.location_by_cluster = self.customer_with_behavior_and_clusters.groupby(['Cluster', 'Location']).size().unstack(fill_value=0)
        print("Data preprocessing completed.")

    def get_coordinates(self, address, retries=3, delay=2):
        geolocator = Photon(user_agent='geoapi')  # Initialize Photon object
        for attempt in range(retries):
            try:
                result = geolocator.geocode(address, timeout=10)  # Set a longer timeout if needed
                if result:
                    return result.latitude, result.longitude
            except GeocoderTimedOut:
                print(f"Timeout error on {address}, retrying... (Attempt {attempt+1} of {retries})")
                sleep(delay)  # Add a delay before retrying
            except Exception as e:
                print(f"Error on {address}: {e}")
                break
        return None, None

    def geocode_locations(self):
        # Geocode each unique location
        unique_locations = self.location_by_cluster.columns
        for location in tqdm(unique_locations, total=len(unique_locations), desc=' > Generating coordinates...'):
            # Add a small delay between requests to avoid rate limits
            sleep(1)
            latitude, longitude = self.get_coordinates(location)
            self.location_coordinates[location] = {'latitude': latitude, 'longitude': longitude}
        print(">> Location geocoding completed.\n")

    def generate_heatmaps(self):
        # Initialize a list to store heatmap data for each location and cluster
        heatmap_data = []

        # Loop through each location in location_by_cluster
        for location in self.location_by_cluster.columns:
            coords = self.location_coordinates.get(location)
            if coords and coords['latitude'] and coords['longitude']:
                for cluster in self.location_by_cluster.index:
                    customer_count = self.location_by_cluster.loc[cluster, location]
                    heatmap_data.append([coords['latitude'], coords['longitude'], customer_count])

        # Ensure the latitude, longitude, and customer count are converted to standard Python types (float and int)
        heatmap_data_cleaned = [[float(lat), float(lon), int(count)] for lat, lon, count in heatmap_data]
        
        return heatmap_data_cleaned

    def create_heatmaps(self):
        # Generate heatmaps for each cluster
        clusters = self.location_by_cluster.index
        for cluster in clusters:
            # Initialize the Folium map centered at the USA
            m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

            # Prepare the heatmap data for this cluster
            heatmap_data_cluster = []
            for location in self.location_by_cluster.columns:
                coords = self.location_coordinates.get(location)
                if coords and coords['latitude'] and coords['longitude']:
                    customer_count = self.location_by_cluster.loc[cluster, location]
                    heatmap_data_cluster.append([coords['latitude'], coords['longitude'], int(customer_count)])

            # Create a heatmap for this cluster
            HeatMap(
                heatmap_data_cluster,
                max_zoom=10,
                radius=20,
                blur=10,
                gradient={
                    0.1: 'blue', 0.2: '#add8e6', 0.3: 'green', 0.4: 'yellow',
                    0.5: '#ffa07a', 0.6: 'orange', 0.7: 'red', 0.9: 'darkred', 1.0: 'purple'
                }
            ).add_to(m)

            # Save each map to an HTML file
            m.save(f'heatmaps/heatmap_cluster_{int(cluster)}.html')
            print(f">> HTML file for Cluster {int(cluster)}'s Heat Map successfully saved!")

if __name__ == "__main__":
    # Instantiate the class
    heatmap_generator = HeatmapGenerator()

    # Step 1: Preprocess the data
    heatmap_generator.preprocess_data()

    # Step 2: Geocode the unique locations
    heatmap_generator.geocode_locations()

    # Step 3: Generate and save heatmaps
    heatmap_generator.create_heatmaps()