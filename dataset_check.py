import pandas as pd

# Load dataset
data = pd.read_csv("brisbane_water_quality.csv")

# Show first 5 rows
print(data.head())

# Show column names
print("\nColumns in dataset:")
print(data.columns)
