import matplotlib.pyplot as plt
import numpy as np

# --- Replace these lists with your actual metrics from your project ---
targets = ['pH', 'Temperature', 'DO', 'Turbidity', 'Salinity']

# Example MAE values (replace with your project's actual MAE values)
train_mae = [0.12, 0.15, 0.10, 0.08, 0.09]
val_mae   = [0.14, 0.17, 0.11, 0.10, 0.12]

# X positions for the bars
x = np.arange(len(targets))
width = 0.35

# Create the bar chart
plt.figure(figsize=(10,6))
plt.bar(x - width/2, train_mae, width, label='Training MAE', color='#1f77b4')
plt.bar(x + width/2, val_mae, width, label='Validation MAE', color='#ff7f0e')

plt.xticks(x, targets)
plt.ylabel('Mean Absolute Error (MAE)')
plt.title('Training vs Validation Performance')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Save the figure directly as an image for thesis
plt.savefig('Training_Validation_Performance.png', dpi=300, bbox_inches='tight')
plt.show()