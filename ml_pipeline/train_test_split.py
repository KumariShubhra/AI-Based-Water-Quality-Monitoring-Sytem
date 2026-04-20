import pandas as pd
from sklearn.model_selection import train_test_split

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

y = X.apply(water_label, axis=1)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Training size:", X_train.shape)
print("Testing size:", X_test.shape)
