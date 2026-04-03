import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# 1. Generate Synthetic Physics Data (v = a * t)
# Let's assume the true acceleration 'a' is 9.8 m/s^2 (gravity)
true_a = 9.8
t = np.linspace(0, 10, 100).reshape(-1, 1)  # 100 time points from 0-10s
noise = np.random.normal(0, 2, t.shape)      # Add some "measurement error"
v = true_a * t + noise                       # v = at + noise

# 2. Initialize and Train the Model
# We use Linear Regression to find the best-fit line
model = LinearRegression(fit_intercept=False) 
model.fit(t, v)

# 3. Extract the "Learned" Physics Constant
learned_a = model.coef_[0][0]
print(f"True Acceleration: {true_a} m/s²")
print(f"ML Predicted Acceleration: {learned_a:.2f} m/s²")

# 4. Visualization
plt.scatter(t, v, color='blue', label='Observed Data (with noise)', s=10)
plt.plot(t, model.predict(t), color='red', label=f'ML Fit: v = {learned_a:.2f}t')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.title('Using ML to Determine Acceleration')
plt.legend()
plt.show()