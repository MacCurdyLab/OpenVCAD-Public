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

# Sinusoidal modulus oscillation along X
frequency = 0.5
mod_base = 5.0
mod_amplitude = 4.0
sin_expr = f'{mod_base} + {mod_amplitude} * sin({frequency} * x)'

# Color bands: map a sine wave to the red channel for striped color
color_freq = 0.8
r_expr = f'0.5 * sin({color_freq} * x) + 0.5'
g_expr = '0.2'
b_expr = f'0.5 * sin({color_freq} * x + 3.14159) + 0.5'
a_expr = '1.0'

# --- Build Object ---
prism = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(length, width, height))

prism.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(sin_expr))

color_attr = pv.Vec4Attribute(r_expr, g_expr, b_expr, a_expr)
prism.set_attribute(pv.DefaultAttributes.COLOR_RGBA, color_attr)

root = prism
viz.Render(root)

# --- Matplotlib Plot ---
x = np.linspace(-half_len, half_len, 300)
sin_y = mod_base + mod_amplitude * np.sin(frequency * x)
color_r = 0.5 * np.sin(color_freq * x) + 0.5
color_b = 0.5 * np.sin(color_freq * x + np.pi) + 0.5

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

ax1.plot(x, sin_y, linewidth=2, color='tab:blue')
ax1.set_ylabel('Modulus (MPa)')
ax1.set_title('Sinusoidal Modulus Oscillation')
ax1.grid(True, alpha=0.3)

ax2.plot(x, color_r, label='Red', linewidth=2, color='red')
ax2.plot(x, color_b, label='Blue', linewidth=2, color='blue')
ax2.axhline(0.2, label='Green', linewidth=2, color='green', linestyle='--')
ax2.set_xlabel('x (mm)')
ax2.set_ylabel('Channel Value [0–1]')
ax2.set_title('Periodic Color Bands (RGBA Channels)')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
_guide_images = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "source", "guides", "images"))
plot_path = os.path.join(_guide_images, "03_periodic_plot.png")
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.show()
