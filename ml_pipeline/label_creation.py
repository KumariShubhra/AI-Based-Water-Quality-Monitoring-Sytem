import pandas as pd

data = pd.read_csv("brisbane_water_quality.csv")

X = data[['pH', 'Temperature', 'Dissolved Oxygen', 'Turbidity', 'Salinity']]
X = X.fillna(X.mean())

def water_label(row):
    if (6.5 <= row['pH'] <= 8.5 and
        row['Turbidity'] <= 5 and
        row['Dissolved Oxygen'] >= 5):
        return 1
    else:
        return 0

labels = X.apply(water_label, axis=1)

print("Label count:")
print(labels.value_counts())
