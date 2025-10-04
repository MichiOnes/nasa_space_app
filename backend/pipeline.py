#%%
import re
import random
import json


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime



data_path = 'C:/Users/juanj/OneDrive/Documentos/GitHub/nasa_space_app/backend/data/final_data.npz'
data = np.load(data_path)


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

#%%

def monthly_quartiles_hemispheres(data, antarctic_cutoff=-60):
    """
    Compute monthly quartiles for each variable per hemisphere, excluding Antarctica.

    Parameters:
        data : dict
            Dictionary containing variables with dimensions (time, lat, lon) and 'lat', 'lon', 'time'
        antarctic_cutoff : float
            Latitude below which data are excluded (default -60°)

    Returns:
        monthly_quartiles_df : pd.DataFrame
            MultiIndex DataFrame with index (Variable, Hemisphere, Month)
            Columns: ['Min', 'Q1', 'Median', 'Q3', 'Max']
    """

    # Time index
    time_len = len(data['time'])
    start_year = 1940
    time_index = np.array([datetime.datetime(start_year + i//12, (i%12)+1, 1) for i in range(time_len)])
    months = np.array([t.month for t in time_index])

    latitudes = data['lat']
    north_idx = np.where(latitudes >= 0)[0]
    south_idx = np.where((latitudes < 0) & (latitudes > antarctic_cutoff))[0]  # exclude Antarctica

    monthly_quartiles_hem = {}

    for key, value in data.items():
        if isinstance(value, np.ndarray) and key not in ['lat', 'lon', 'time']:
            monthly_quartiles_hem[key] = {'Northern': {}, 'Southern': {}}

            for m in range(1, 13):
                # Northern Hemisphere
                arr_north = value[months == m][:, north_idx, :].flatten()
                arr_north = arr_north[~np.isnan(arr_north)]
                if len(arr_north) > 0:
                    Q1 = np.percentile(arr_north, 25)
                    Q3 = np.percentile(arr_north, 75)
                    IQR = Q3 - Q1
                    arr_north = np.clip(arr_north, Q1 - 1.5*IQR, Q3 + 1.5*IQR)
                    q_north = np.percentile(arr_north, [0, 25, 50, 75, 100])
                else:
                    q_north = [np.nan]*5

                # Southern Hemisphere
                arr_south = value[months == m][:, south_idx, :].flatten()
                arr_south = arr_south[~np.isnan(arr_south)]
                if len(arr_south) > 0:
                    Q1 = np.percentile(arr_south, 25)
                    Q3 = np.percentile(arr_south, 75)
                    IQR = Q3 - Q1
                    arr_south = np.clip(arr_south, Q1 - 1.5*IQR, Q3 + 1.5*IQR)
                    q_south = np.percentile(arr_south, [0, 25, 50, 75, 100])
                else:
                    q_south = [np.nan]*5

                monthly_quartiles_hem[key]['Northern'][m] = q_north
                monthly_quartiles_hem[key]['Southern'][m] = q_south

    # Convert to MultiIndex DataFrame
    dfs = []
    for key, hemi_dict in monthly_quartiles_hem.items():
        for hemi, month_dict in hemi_dict.items():
            df = pd.DataFrame(month_dict).T  # rows = months
            df.columns = ['Min', 'Q1', 'Median', 'Q3', 'Max']
            df.index.name = 'Month'
            df['Variable'] = key
            df['Hemisphere'] = hemi
            dfs.append(df.reset_index())

    monthly_quartiles_df = pd.concat(dfs, axis=0).set_index(['Variable','Hemisphere','Month'])
    return monthly_quartiles_df

monthly_quartiles_df = monthly_quartiles_hemispheres(data, antarctic_cutoff=-60)

# Example: Median temperature in Northern Hemisphere for July
monthly_quartiles_df.loc[('temperature','Northern',7), 'Median']

#%%
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

# Create colormap: first color for ocean, rest for other clusters
k_final = len(unique_clusters)
colors = plt.get_cmap('tab10', k_final).colors
# Ensure ocean is first color
colors = np.vstack(([0, 0.3, 0.8, 1], colors[1:]))  
new_cmap = ListedColormap(colors)

cluster_names = ['Ocean', 'Continental', 'Frozen water', 'Desertic', 'Tropical', 'Arid', 'Artic', 'Template']


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
    cluster_num = int(cluster_num)

    # Return cluster name safely
    if 0 <= cluster_num < len(cluster_names):
        return cluster_names[cluster_num]

    
lat_input = 55   # Moscu
lon_input = 37

climate = get_climate_at_location(lat_input, lon_input)
# print(f'Climate at lat={lat_input}, lon={lon_input}: {climate}') #Moscu

txt = """
Category: Corn – Industrial Scale

Q1: In your region, which water management strategy is most suitable for corn?
A) Retain water in soil using compost. (Continental)
B) Use drip irrigation and reflective mulch. (Desert)
C) Use raised beds and drainage channels. (Tropical)
D) Collect rainwater and irrigate in furrows. (Arid)
E) Grow under greenhouses. (Arctic)
F) Mulch and schedule irrigation. (Temperate)
fb) precipitation, soil_moisture

Q2: In your region, which fertilization strategy is most appropriate?
A) Compost and green manures. (Continental)
B) Slow-release fertilizer in small doses. (Desert)
C) Biofertilizers and compost. (Tropical)
D) Organic matter plus precise fertilizer. (Arid)
E) Soluble nutrients in protected structures. (Arctic)
F) Crop rotation with legumes and compost. (Temperate)
fb) soil_moisture, evaporation

Q3: In your region, which practice best prevents soil erosion?
A) No-till with buffer strips. (Continental)
B) Windbreaks and ground cover. (Desert)
C) Intercropping and terraces. (Tropical)
D) Contour furrows and ditches. (Arid)
E) Raised greenhouse beds. (Arctic)
F) Mulch and minimum tillage. (Temperate)
fb) wind, temperature

Q4: In your region, which approach helps corn adapt to climate variability?
A) Adjust sowing dates and use resilient varieties. (Continental)
B) Drought-tolerant hybrids and efficient irrigation. (Desert)
C) Multiple varieties and polyculture. (Tropical)
D) Mulch and drought-tolerant crops. (Arid)
E) Protected structures. (Arctic)
F) Adapted hybrids and optimized irrigation/nutrients. (Temperate)
fb) temperature, precipitation

Q5: In your region, which method increases corn yield sustainably?
A) Rotate with legumes and use compost. (Continental)
B) Precise irrigation and fertilization. (Desert)
C) Compost, biofertilizers, integrated pest management. (Tropical)
D) Strip planting with drought-tolerant varieties. (Arid)
E) Controlled structures. (Arctic)
F) Mulch, minimum tillage, optimized irrigation. (Temperate)
fb) soil_moisture, precipitation

Category: Corn – Small-Scale / Household

Q1: In your region, which water management strategy is most suitable for your small corn plot?
A) Manual watering and mulch. (Continental)
B) Small drip system and soil cover. (Desert)
C) Mini raised beds and drainage channels. (Tropical)
D) Capture rainwater and irrigate in furrows. (Arid)
E) Pots or small greenhouses. (Arctic)
F) Water during cooler hours and add compost. (Temperate)
fb) precipitation, soil_moisture

Q2: In your region, which fertilization strategy is most appropriate for your small corn plot?
A) Homemade compost and kitchen scraps. (Continental)
B) Small, timed doses of organic fertilizer. (Desert)
C) Mix biofertilizers and compost. (Tropical)
D) Slow-release fertilizer with organic matter. (Arid)
E) Foliar nutrients in pots or protected beds. (Arctic)
F) Rotate with legumes and add compost manually. (Temperate)
fb) soil_moisture, evaporation

Q3: In your region, which practice best prevents soil erosion in your small corn plot?
A) Manual no-till with vegetative barriers. (Continental)
B) Cover soil and small fences to reduce wind. (Desert)
C) Intercrop and use mulch. (Tropical)
D) Hand-made furrows and terraces. (Arid)
E) Raised beds or small greenhouses. (Arctic)
F) Mulch and minimal tillage. (Temperate)
fb) wind, temperature

Q4: In your region, which approach helps your small corn plot adapt to climate variability?
A) Adjust sowing dates and use resilient varieties. (Continental)
B) DIY irrigation and drought-tolerant varieties. (Desert)
C) Polyculture and resistant varieties. (Tropical)
D) Mulch and drought-tolerant crops. (Arid)
E) Protect plants in small greenhouses or raised beds. (Arctic)
F) Choose adapted varieties and manage irrigation/fertilization manually. (Temperate)
fb) temperature, precipitation

Q5: In your region, which method increases productivity sustainably in your small corn plot?
A) Rotate crops and apply compost manually. (Continental)
B) Measure soil moisture and apply targeted fertilizer. (Desert)
C) Compost, biofertilizers, hand-managed pest control. (Tropical)
D) Efficient watering and small furrows. (Arid)
E) Pots, raised beds, or small greenhouses with nutrients. (Arctic)
F) Minimum tillage, mulch, and manual irrigation. (Temperate)
fb) soil_moisture, precipitation

Category: Tomato – Industrial Scale

Q1: In your region, which water management strategy is most suitable for tomato?
A) Timed irrigation and mulch. (Continental)
B) Sensor-driven drip irrigation and reflective covers. (Desert)
C) Raised beds and drainage channels. (Tropical)
D) Harvest rainwater and strip irrigation. (Arid)
E) Grow under controlled greenhouses. (Arctic)
F) Scheduled irrigation with organic amendments. (Temperate)
fb) precipitation, soil_moisture

Q2: In your region, which fertilization strategy is most suitable for tomato?
A) Compost and soil-tested fertilizers. (Continental)
B) Slow-release fertilizers and green manures. (Desert)
C) Compost and biofertilizers. (Tropical)
D) Organic matter with precise fertilization. (Arid)
E) Soluble nutrients in greenhouse beds. (Arctic)
F) Rotate crops with legumes and organic fertilizers. (Temperate)
fb) soil_moisture, evaporation

Q3: In your region, which practice best prevents soil erosion in tomato fields?
A) Minimum tillage and buffer strips. (Continental)
B) Soil cover and windbreaks. (Desert)
C) Intercropping and terraces. (Tropical)
D) Terraces and infiltration ditches. (Arid)
E) Raised greenhouse beds. (Arctic)
F) Mulch and mechanized minimum tillage. (Temperate)
fb) wind, temperature

Q4: In your region, which approach helps tomato crops adapt to climate variability?
A) Adjust planting dates and resilient varieties. (Continental)
B) Drought-tolerant varieties and efficient irrigation. (Desert)
C) Multiple varieties and polyculture. (Tropical)
D) Mulch and drought-tolerant crops. (Arid)
E) Protected structures. (Arctic)
F) Adapted hybrids and optimized irrigation/nutrient management. (Temperate)
fb) precipitation, temperature

Q5: In your region, which method increases tomato yield sustainably?
A) Rotate crops and use compost. (Continental)
B) Precise irrigation and fertilization. (Desert)
C) Compost, biofertilizers, integrated pest management. (Tropical)
D) Strip planting and drought-tolerant varieties. (Arid)
E) Controlled structures. (Arctic)
F) Mulch, minimum tillage, optimized irrigation. (Temperate)
fb) soil_moisture, precipitation
    
Category: Wheat – Industrial Scale

Q1: In your region, which water management strategy is most suitable for wheat?
A) Deep tillage and organic amendments. (Continental)
B) Sensor-driven drip irrigation. (Desert)
C) Raised beds and drainage channels. (Tropical)
D) Capture rainwater and irrigate in furrows. (Arid)
E) Protected greenhouses. (Arctic)
F) Scheduled irrigation with mulch/organic matter. (Temperate)
fb) precipitation, soil_moisture

Q2: In your region, which fertilization strategy is most suitable for wheat?
A) Compost and soil-tested fertilizers. (Continental)
B) Slow-release fertilizers and green manures. (Desert)
C) Compost and biofertilizers. (Tropical)
D) Organic matter plus precise fertilizer. (Arid)
E) Soluble nutrients in greenhouse beds. (Arctic)
F) Crop rotation with legumes and compost. (Temperate)
fb) temperature, precipitation

Q3: In your region, which practice best prevents soil erosion in wheat fields?
A) Minimum tillage and buffer strips. (Continental)
B) Soil cover and windbreaks. (Desert)
C) Intercropping and terraces. (Tropical)
D) Terraces and retention ditches. (Arid)
E) Raised greenhouse beds. (Arctic)
F) Mulch and minimum tillage. (Temperate)
fb) wind, soil_moisture

Q4: In your region, which approach helps wheat adapt to climate variability?
A) Adjust sowing dates and resilient varieties. (Continental)
B) Drought-tolerant varieties and efficient irrigation. (Desert)
C) Polyculture and multiple varieties. (Tropical)
D) Mulch and drought-tolerant crops. (Arid)
E) Protected greenhouses. (Arctic)
F) Adapted hybrids and integrated irrigation/fertilization. (Temperate)
fb) frost_days, heat_days

Q5: In your region, which method increases wheat yield sustainably?
A) Rotate crops and use compost. (Continental)
B) Precise irrigation and fertilization. (Desert)
C) Compost, biofertilizers, integrated pest management. (Tropical)
D) Strip planting with drought-tolerant varieties. (Arid)
E) Controlled structures. (Arctic)
F) Mulch, minimum tillage, optimized irrigation. (Temperate)
fb) soil_moisture, temperature

Category: Wheat – Small-Scale / Household

Q1: In your region, which water management strategy is most suitable for your small wheat plot?
A) Manual watering and mulch. (Continental)
B) Small drip system. (Desert)
C) Mini raised beds and drainage channels. (Tropical)
D) Capture rainwater and irrigate in furrows. (Arid)
E) Pots or mini-greenhouses. (Arctic)
F) Water during cooler hours and add compost. (Temperate)
fb) precipitation, soil_moisture

Q2: In your region, which fertilization strategy is most suitable for your small wheat plot?
A) Homemade compost. (Continental)
B) Small, timed doses of organic fertilizer. (Desert)
C) Mix biofertilizers and compost. (Tropical)
D) Slow-release fertilizer with organic matter. (Arid)
E) Foliar nutrients and compost in pots/raised beds. (Arctic)
F) Rotate with legumes and add compost manually. (Temperate)
fb) temperature, precipitation

Q3: In your region, which practice best prevents soil erosion in your small wheat plot?
A) Manual no-till with vegetative barriers. (Continental)
B) Cover soil and small fences. (Desert)
C) Intercrop and mulch. (Tropical)
D) Hand-made terraces and furrows. (Arid)
E) Raised beds or mini-greenhouses. (Arctic)
F) Mulch and minimum tillage. (Temperate)
fb) wind, soil_moisture

Q4: In your region, which approach helps your small wheat plot adapt to climate variability?
A) Adjust planting dates and resilient varieties. (Continental)
B) DIY irrigation and drought-tolerant varieties. (Desert)
C) Polyculture and diverse varieties. (Tropical)
D) Mulch and drought-tolerant crops. (Arid)
E) Protect plants in small greenhouses or raised beds. (Arctic)
F) Adapted varieties and manual irrigation/fertilization. (Temperate)
fb) frost_days, heat_days


Q5: In your region, which method increases productivity sustainably in your small wheat plot?
A) Rotate crops and apply compost manually. (Continental)
B) Measure soil moisture and apply targeted fertilizer. (Desert)
C) Compost, biofertilizers, hand-managed pest control. (Tropical)
D) Efficient watering and small furrows. (Arid)
E) Pots, raised beds, mini-greenhouses with nutrients. (Arctic)
F) Minimum tillage, mulch, manual irrigation. (Temperate)
fb) soil_moisture, temperature

Category: Wheat – Small-Scale / Household

Q1: In your region, which water management strategy is most suitable for your small wheat plot?
A) Water manually and apply mulch. (Continental)
B) Set up a small drip system to conserve water. (Desert)
C) Build mini raised beds and drainage channels. (Tropical)
D) Capture rainwater and irrigate in furrows. (Arid)
E) Grow in pots or mini-greenhouses to extend the season. (Arctic)
F) Water during cooler hours and add compost. (Temperate)
fb) precipitation, soil_moisture

Q2: In your region, which fertilization strategy is most suitable for your small wheat plot?
A) Apply homemade compost and kitchen scraps. (Continental)
B) Apply small, timed doses of organic fertilizer. (Desert)
C) Mix biofertilizers and compost. (Tropical)
D) Apply slow-release fertilizer with organic matter. (Arid)
E) Provide foliar nutrients and compost in pots or raised beds. (Arctic)
F) Rotate with legumes and add compost manually. (Temperate)
fb) temperature, precipitation

Q3: In your region, which practice best prevents soil erosion in your small wheat plot?
A) Manual no-till with vegetative barriers. (Continental)
B) Cover soil and use small fences to reduce wind erosion. (Desert)
C) Intercrop and apply mulch. (Tropical)
D) Hand-made terraces and furrows. (Arid)
E) Plant in raised beds or mini-greenhouses. (Arctic)
F) Apply mulch and minimal tillage. (Temperate)
fb) wind, soil_moisture

Q4: In your region, which approach helps your small wheat plot adapt to climate variability?
A) Adjust planting dates and resilient varieties. (Continental)
B) DIY irrigation and drought-tolerant varieties. (Desert)
C) Polyculture and diverse varieties. (Tropical)
D) Mulch and drought-tolerant crops. (Arid)
E) Protect plants in small greenhouses or raised beds. (Arctic)
F) Adapted varieties and manual irrigation/fertilization. (Temperate)
fb) frost_days, heat_days

Q5: In your region, which method increases productivity sustainably in your small wheat plot?
A) Rotate crops and apply compost manually. (Continental)
B) Measure soil moisture and apply targeted fertilizer. (Desert)
C) Compost, biofertilizers, hand-managed pest control. (Tropical)
D) Efficient watering and small furrows. (Arid)
E) Pots, raised beds, mini-greenhouses with nutrients. (Arctic)
F) Minimum tillage, mulch, manual irrigation. (Temperate)
fb) soil_moisture, temperature
"""
import re
import random
import json

# --------------------------
# CLIMATE CONFIGURATION
# --------------------------
cluster_names = ['Ocean', 'Continental', 'Frozen water', 'Desertic', 'Tropical', 'Arid', 'Artic', 'Template']
climate_dict = {
    "Ocean": 0,
    "Continental": 1,
    "Frozen water": 0,
    "Desertic": 2,
    "Tropical": 3,
    "Arid": 4,
    "Artic": 5,
    "Template": 6
}

# --------------------------
# PARSER
# --------------------------
def parse_questions(text):
    categories = {}
    current_category = "Default"
    
    lines = text.strip().split("\n")
    qid, qtext, answers, feedback = None, None, {}, None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        cat_match = re.match(r"Category:\s*(.*)", line)
        if cat_match:
            current_category = cat_match.group(1).strip()
            categories[current_category] = {}
            continue
        
        q_match = re.match(r"(Q\d+):\s*(.*)", line)
        if q_match:
            if qid:
                categories[current_category][qid] = {"text": qtext, **answers, "fb": feedback}
            qid, qtext = q_match.groups()
            answers = {}
            feedback = None
            continue
        
        a_match = re.match(r"([A-F])\)\s*(.*)", line)
        if a_match:
            letter, ans_text = a_match.groups()
            ans_text = re.sub(r"\s*\([^)]*\)", "", ans_text).strip()
            idx = ord(letter) - ord('A') + 1
            answers[f"s{idx}"] = ans_text
            continue
        
        fb_match = re.match(r"fb\)\s*(.*)", line)
        if fb_match:
            feedback = fb_match.group(1).strip().split(",")
            continue
    
    if qid:
        categories[current_category][qid] = {"text": qtext, **answers, "fb": feedback}
    
    return categories

# --------------------------
# QUIZ GENERATOR
# --------------------------
def build_quiz_objects(categories_dict, user_climate, num_options=4):
    quiz_list = []
    climate_idx = climate_dict.get(user_climate, None)
    if climate_idx is None or climate_idx == 0:
        return []

    for cat, questions in categories_dict.items():
        for qid, qdata in questions.items():
            correct_key = f"s{climate_idx}"
            correct_answer = qdata.get(correct_key)
            if not correct_answer:
                continue
            
            all_answers = [v for k, v in qdata.items() if k.startswith("s")]
            wrong_answers = [a for a in all_answers if a != correct_answer]
            selected_wrongs = random.sample(wrong_answers, min(num_options-1, len(wrong_answers)))
            options = selected_wrongs + [correct_answer]
            random.shuffle(options)
            option_labels = [chr(65+i) for i in range(len(options))]
            options_dict = dict(zip(option_labels, options))
            correct_label = [k for k, v in options_dict.items() if v == correct_answer][0]
            
            quiz_list.append({
                "category": cat,
                "qid": qid,
                "text": qdata["text"],
                "options": options_dict,
                "answer": correct_label,
                "fb": qdata.get("fb", [])
            })
    return quiz_list

# --------------------------
# RUN PARSER & GENERATOR
# --------------------------
categories_dict = parse_questions(txt)  # txt = your question text
user_climate = "Desertic"
quiz_for_app = build_quiz_objects(categories_dict, user_climate, num_options=4)

# --------------------------
# TEST OUTPUT
# --------------------------
print("Categories parsed:", categories_dict.keys())
print("Number of quiz questions for app:", len(quiz_for_app))
if quiz_for_app:
    print(json.dumps(quiz_for_app[0], indent=2, ensure_ascii=False))
