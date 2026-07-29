import os
import pyvcad as pv
import pyvcad_rendering as viz
import matplotlib.pyplot as plt
import numpy as np

# --- Parameters ---
sph_radius = 15.0

# Radial gradient: modulus increases from center (r=0) to surface (r=R)
mod_min = 1.0
mod_max = 10.0
radial_expr = f'{mod_min} + ({mod_max} - {mod_min}) * (r / {sph_radius})'

# Polar angle gradient: color varies from north pole (phis=0) to south pole (phis=pi)
# Normalize phis from [0, pi] to [0, 1]
r_expr = f'clamp(phis / 3.14159, 0, 1)'
g_expr = '0.2'
b_expr = f'clamp(1.0 - phis / 3.14159, 0, 1)'
a_expr = '1.0'

# Volume fractions: radial blend from center to surface
materials = pv.default_materials
vf_outer = f'clamp(r / {sph_radius}, 0, 1)'
vf_inner = f'1.0 - clamp(r / {sph_radius}, 0, 1)'

# --- Build Object ---
sphere = pv.Sphere(pv.Vec3(0, 0, 0), sph_radius)

# Radial modulus
sphere.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(radial_expr))

# Polar color
color_attr = pv.Vec4Attribute(r_expr, g_expr, b_expr, a_expr)
sphere.set_attribute(pv.DefaultAttributes.COLOR_RGBA, color_attr)

# Volume fractions
vf_attr = pv.VolumeFractionsAttribute([
    (vf_outer, materials.id("red")),
    (vf_inner, materials.id("blue"))
])
sphere.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, vf_attr)

root = sphere
viz.Render(root, materials)

# --- Matplotlib Plots ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Radial gradient
r_vals = np.linspace(0, sph_radius, 200)
mod_y = mod_min + (mod_max - mod_min) * (r_vals / sph_radius)

ax1.plot(r_vals, mod_y, linewidth=2, color='tab:blue')
ax1.set_xlabel('r (mm)')
ax1.set_ylabel('Modulus (MPa)')
ax1.set_title('Radial Gradient (r)')
ax1.grid(True, alpha=0.3)

# Polar angle gradient: show as 2D semicircle cross-section
theta_plot = np.linspace(0, np.pi, 200)
r_plot = np.linspace(0, 1, 100)
Theta, R = np.meshgrid(theta_plot, r_plot)

# Color value depends only on polar angle (phis)
color_val = np.clip(Theta / np.pi, 0, 1)

x_plot = R * np.sin(Theta)
z_plot = R * np.cos(Theta)

im = ax2.pcolormesh(x_plot, z_plot, color_val, cmap='RdBu_r', shading='auto')
ax2.set_xlabel('x / R')
ax2.set_ylabel('z / R')
ax2.set_title('Polar Angle Color Gradient (phis)')
ax2.set_aspect('equal')
plt.colorbar(im, ax=ax2, label='Red channel')

plt.tight_layout()
_guide_images = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "source", "guides", "images"))
plot_path = os.path.join(_guide_images, "07_spherical_plot.png")
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.show()
