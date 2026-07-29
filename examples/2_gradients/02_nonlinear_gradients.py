import os
import pyvcad as pv
import pyvcad_rendering as viz
import matplotlib.pyplot as plt
import numpy as np

# --- Parameters ---
length = 50.0
width = 10.0
height = 10.0
half_len = length / 2.0

# Sigmoid: smooth transition along X
k = 0.2
sig_min = 1.0
sig_max = 10.0
sigmoid_expr = f'{sig_min} + ({sig_max} - {sig_min}) / (1 + exp(-{k} * x))'

# Gaussian: bell curve centered at origin along X
amplitude = 10.0
sigma = 10.0
gaussian_expr = f'{amplitude} * exp(-(x^2) / (2 * {sigma}^2))'

# Exponential decay: starts high at -half_len, decays toward +half_len
decay_rate = 0.06
exp_amplitude = 10.0
exponential_expr = f'{exp_amplitude} * exp(-{decay_rate} * (x + {half_len}))'

# --- Build Object ---
prism = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(length, width, height))

# Sigmoid -> modulus
prism.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(sigmoid_expr))

# Gaussian -> temperature
prism.set_attribute(pv.DefaultAttributes.TEMPERATURE, pv.FloatAttribute(gaussian_expr))

# Exponential decay -> density
prism.set_attribute(pv.DefaultAttributes.DENSITY, pv.FloatAttribute(exponential_expr))

root = prism
viz.Render(root)

# --- Matplotlib Plot ---
x = np.linspace(-half_len, half_len, 300)
sig_y = sig_min + (sig_max - sig_min) / (1 + np.exp(-k * x))
gauss_y = amplitude * np.exp(-(x**2) / (2 * sigma**2))
exp_y = exp_amplitude * np.exp(-decay_rate * (x + half_len))

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, sig_y, label=f'Sigmoid (k={k})', linewidth=2)
ax.plot(x, gauss_y, label=f'Gaussian (sigma={sigma})', linewidth=2, linestyle='--')
ax.plot(x, exp_y, label=f'Exponential Decay (rate={decay_rate})', linewidth=2, linestyle=':')
ax.set_xlabel('x (mm)')
ax.set_ylabel('Attribute Value')
ax.set_title('Non-Linear Gradients Along X')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(-half_len, half_len)

_guide_images = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "source", "guides", "images"))
plot_path = os.path.join(_guide_images, "02_nonlinear_plot.png")
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.show()
