import pandas as pd

data = pd.read_csv("brisbane_water_quality.csv")

features = data[['pH', 'Temperature', 'Dissolved Oxygen', 'Turbidity', 'Salinity']]
features = features.fillna(features.mean())

print("Selected features:")
print(features.head())
