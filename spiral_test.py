import numpy as np
import matplotlib.pyplot as plt

def generate_logarithmic_spiral(a, b, theta_max, num_points):
    theta = np.linspace(0, theta_max, num_points)
    r = a * np.exp(b * theta)
    x = -1 * r * np.cos(theta)
    y = -1 * r * np.sin(theta)
    return x, y

# Parameters
a = 0.05  # Scale factor
b = 0.15  # Growth rate
theta_max = (8 * np.pi)  # Maximum angle (adjust for desired length of the spiral)
num_points = 400  # Number of points along the spiral

# Generate spiral points
x, y = generate_logarithmic_spiral(a, b, theta_max, num_points)

# Plot
plt.figure(figsize=(8, 8))
plt.plot(x, y)
plt.gca().set_aspect('equal', adjustable='box')
plt.title('Logarithmic Spiral')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
plt.show()

