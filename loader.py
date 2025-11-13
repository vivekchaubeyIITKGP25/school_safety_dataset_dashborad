import os
import pandas as pd

def load_all_cities(data_folder="../data"):
    cities = {}

    for file in os.listdir(data_folder):
        if file.endswith(".json"):
            path = os.path.join(data_folder, file)
            city_name = file.split("_")[0]  # city name

            if city_name not in cities:
                cities[city_name] = {}

            if "overall" in file:
                cities[city_name]["overall"] = pd.read_json(path)
            elif "pedestrian" in file:
                cities[city_name]["pedestrian"] = pd.read_json(path)
            elif "final" in file:
                cities[city_name]["final"] = pd.read_json(path)

    # merge city data
    all_cities = []
    for city, data in cities.items():
        df = data["overall"]
        df["pedestrian_safety_index"] = data["pedestrian"]["pedestrian_safety_index"]
        df["traffic_light"] = data["final"]["traffic_light"]
        df["crosswalk"] = data["final"]["crosswalk"]
        df["city"] = city.capitalize()
        all_cities.append(df)

    master_df = pd.concat(all_cities, ignore_index=True)
    return master_df
