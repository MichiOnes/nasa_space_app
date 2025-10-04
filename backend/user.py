from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd


data = np.load('C:/Users/juanj/OneDrive/Documentos/GitHub/nasa_space_app/backend/data/final_data.npz')

# Define Antarctic cutoff
antarctic_cutoff = -60  # degrees latitude

# Get indices for latitudes above cutoff
lat = data['lat']
lat_mask = lat > antarctic_cutoff
lat_filtered = lat[lat_mask]

# Function to filter 3D/4D arrays along lat dimension
def remove_antarctica(array):
    # Assume array shape is (time, lat, lon) or (lat, lon)
    if array.ndim == 3:  # (time, lat, lon)
        return array[:, lat_mask, :]
    elif array.ndim == 2:  # (lat, lon)
        return array[lat_mask, :]
    else:
        return array  # leave 1D arrays like lon unchanged

# Apply to all variables in your dataset
data_filtered = {}
for key, value in data.items():
    if isinstance(value, np.ndarray):
        data_filtered[key] = remove_antarctica(value)
    else:
        data_filtered[key] = value  # lat/lon/time can remain

# Replace lat with filtered latitudes
data_filtered['lat'] = lat_filtered

data = data_filtered.copy()


from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Example variables
vars_to_cluster = ['temperature', 'precipitation', 'frost_days', 'heat_days', 'wind', 'evaporation', 'soil_moisture', 'cloud_cover']

# Prepare lat/lon mask (exclude Antarctica)
lat = data['lat']
lon = data['lon']
lat_mask = lat > -60
lat_filtered = lat[lat_mask]

# Flatten variables and combine
X_list = []
for var in vars_to_cluster:
    var_data = data[var][:, lat_mask, :]  # (time, lat, lon)
    var_mean = np.nanmean(var_data, axis=0)  # mean over time
    X_list.append(var_mean.flatten())

X = np.stack(X_list, axis=1)  # shape = (grid_points, num_variables)

# Remove NaNs
valid_idx = ~np.isnan(X).any(axis=1)
X_clean = X[valid_idx]

# Standardize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_clean)

# Apply k-means
k = 14  # number of climate clusters
kmeans = KMeans(n_clusters=k, random_state=0)
labels = kmeans.fit_predict(X_scaled)

# Reconstruct labels into lat-lon grid
grid_labels = np.full(lat_filtered.size * len(lon), np.nan)
grid_labels[valid_idx] = labels
grid_labels = grid_labels.reshape(len(lat_filtered), len(lon))

#%%
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap

ocean_clusters = [0, 3, 4,6, 7,11,13]
labels_merged = labels.copy()
labels_merged[np.isin(labels_merged, ocean_clusters)] = -1

# Renumber remaining clusters
unique_clusters = np.unique(labels_merged)
cluster_map = {old: new for new, old in enumerate(unique_clusters)}
labels_final = np.array([cluster_map[l] for l in labels_merged])

# Reconstruct lat-lon grid
grid_labels_final = np.full(lat_filtered.size * len(lon), np.nan)
grid_labels_final[valid_idx] = labels_final
grid_labels_final = grid_labels_final.reshape(len(lat_filtered), len(lon))


# Custom legend
cluster_names = ['Ocean', 'Continental', 'Frozen water', 'Desertic', 'Tropical', 'Arid', 'Artic', 'Template']  # adjust length


def get_climate_at_location(lat_input, lon_input, lat_grid=lat_filtered, lon_grid=lon, cluster_grid=grid_labels_final, cluster_names=cluster_names):
    """
    Returns the climate cluster at a given latitude and longitude.

    Parameters:
        lat_input : float
            Latitude of the point
        lon_input : floatgrid_labels_final
            Longitude of the point
        lat_grid : np.array
            1D array of latitudes in the climate grid
        lon_grid : np.array
            1D array of longitudes in the climate grid
        cluster_grid : np.array
            2D array of cluster labels (lat x lon)
        cluster_names : list of str
            Names for each cluster, ordered by cluster number

    Returns:
        cluster_label : str
            Cluster name at the specified location
    """

    # Find nearest indices in grid
    lat_idx = np.abs(lat_grid - lat_input).argmin()
    lon_idx = np.abs(lon_grid - lon_input).argmin()

    # Get cluster number
    cluster_num = cluster_grid[lat_idx, lon_idx]

    # If it's a float, cast to int
    if np.isnan(cluster_num):
        return 'Unknown'
    cluster_num = int(cluster_num)

    # Return cluster name safely
    if 0 <= cluster_num < len(cluster_names):
        return cluster_names[cluster_num]
    else:
        return 'Unknown'


lat_input = 55   # Moscu
lon_input = 37

climate = get_climate_at_location(lat_input, lon_input)

print(f'Climate at lat={lat_input}, lon={lon_input}: {climate}')
