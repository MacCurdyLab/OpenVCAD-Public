import os
import pyvcad as pv
import pyvcad_rendering as viz
import matplotlib.pyplot as plt
import numpy as np

# --- Parameters ---
length = 40.0
width = 10.0
height = 10.0
half_len = length / 2.0

# Modulus gradient along X: linearly maps x in [-half_len, +half_len] to [1, 10] MPa
mod_min = 1.0
mod_max = 10.0
slope = (mod_max - mod_min) / length
offset = (mod_max + mod_min) / 2.0
modulus_expr = f'{slope}*x + {offset}'

# Power-law gradient along X: maps x to [0, 1] range then raises to power n
n = 3.0
power_law_expr = f'({mod_min} + ({mod_max} - {mod_min}) * ((x + {half_len}) / {length}) ^ {n})'

# --- Build Object ---
prism = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(length, width, height))

# Attach the linear gradient as modulus
linear_attr = pv.FloatAttribute(modulus_expr)
prism.set_attribute(pv.DefaultAttributes.MODULUS, linear_attr)

# Attach the power-law gradient as density
power_attr = pv.FloatAttribute(power_law_expr)
prism.set_attribute(pv.DefaultAttributes.DENSITY, power_attr)

root = prism
viz.Render(root)

# --- Matplotlib Plot ---
x = np.linspace(-half_len, half_len, 200)
linear_y = slope * x + offset
power_y = mod_min + (mod_max - mod_min) * ((x + half_len) / length) ** n

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, linear_y, label='Linear', linewidth=2)
ax.plot(x, power_y, label=f'Power Law (n={n})', linewidth=2, linestyle='--')
ax.set_xlabel('x (mm)')
ax.set_ylabel('Attribute Value (MPa)')
ax.set_title('Linear vs Power-Law Gradients Along X')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(-half_len, half_len)

_guide_images = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "source", "guides", "images"))
plot_path = os.path.join(_guide_images, "01_linear_plot.png")
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.show()
