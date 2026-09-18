import matplotlib.pyplot as plt
import numpy as np

epochs = [1, 2, 3]
precision = [0.947316, 0.958940, 0.958833]
recall = [0.954800, 0.962200, 0.966600]
f1 = [0.951043, 0.960567, 0.962701]
accuracy = [0.993442, 0.994645, 0.994917]

plt.style.use('seaborn-v0_8-darkgrid')
plt.figure(figsize=(10, 6))

plt.plot(epochs, accuracy, marker='o', linewidth=3, label='Accuracy', color='#2ecc71')
plt.plot(epochs, f1, marker='s', linewidth=3, label='F1 Score', color='#3498db')
plt.plot(epochs, recall, marker='^', linewidth=2, label='Recall', color='#e74c3c', linestyle='--')
plt.plot(epochs, precision, marker='D', linewidth=2, label='Precision', color='#f39c12', linestyle='--')

plt.title('Model Performance Metrics Over 3 Epochs', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Epoch', fontsize=14, fontweight='bold')
plt.ylabel('Score', fontsize=14, fontweight='bold')
plt.xticks(epochs, fontsize=12)
plt.yticks(fontsize=12)
plt.ylim(0.94, 1.0) 

plt.legend(loc='lower right', fontsize=12, frameon=True, shadow=True)

output_path = '/var/www/model_metrics_graph.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
