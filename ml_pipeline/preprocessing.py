import pandas as pd

# Load dataset
data = pd.read_csv("brisbane_water_quality.csv")

# Select required features
features = data[['pH', 'Temperature', 'Dissolved Oxygen', 'Turbidity', 'Salinity']]

# Check missing values
print("Missing values before preprocessing:")
print(features.isnull().sum())

# Fill missing values with mean
features_filled = features.fillna(features.mean())

print("\nMissing values after preprocessing:")
print(features_filled.isnull().sum())

# Show sample output
print("\nPreprocessed data:")
print(features_filled.head())
