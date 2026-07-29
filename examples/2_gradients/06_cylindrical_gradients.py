import os
import pyvcad as pv
import pyvcad_rendering as viz
import matplotlib.pyplot as plt
import numpy as np

# --- Parameters ---
cyl_radius = 15.0
cyl_height = 30.0

# Radial gradient using rho: stiffness increases from center to edge
mod_min = 1.0
mod_max = 10.0
radial_expr = f'{mod_min} + ({mod_max} - {mod_min}) * (rho / {cyl_radius})'

# Angular gradient using phic: color sweeps around the cylinder
# phic ranges from -pi to +pi, normalize to [0, 1]
r_expr = f'clamp((phic + 3.14159) / (2 * 3.14159), 0, 1)'
g_expr = f'clamp(1.0 - (phic + 3.14159) / (2 * 3.14159), 0, 1)'
b_expr = '0.3'
a_expr = '1.0'

# Volume fractions: radial blend from core to edge
materials = pv.default_materials
vf_edge = f'clamp(rho / {cyl_radius}, 0, 1)'
vf_core = f'1.0 - clamp(rho / {cyl_radius}, 0, 1)'

# --- Build Object ---
cylinder = pv.Cylinder(pv.Vec3(0, 0, 0), cyl_radius, cyl_height)

# Radial modulus
cylinder.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(radial_expr))

# Angular color
color_attr = pv.Vec4Attribute(r_expr, g_expr, b_expr, a_expr)
cylinder.set_attribute(pv.DefaultAttributes.COLOR_RGBA, color_attr)

# Volume fractions
vf_attr = pv.VolumeFractionsAttribute([
    (vf_edge, materials.id("red")),
    (vf_core, materials.id("blue"))
])
cylinder.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, vf_attr)

root = cylinder
viz.Render(root, materials)

# --- Matplotlib Plots ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Radial gradient plot
rho = np.linspace(0, cyl_radius, 200)
mod_y = mod_min + (mod_max - mod_min) * (rho / cyl_radius)

ax1.plot(rho, mod_y, linewidth=2, color='tab:blue')
ax1.set_xlabel('rho (mm)')
ax1.set_ylabel('Modulus (MPa)')
ax1.set_title('Radial Gradient (rho)')
ax1.grid(True, alpha=0.3)

# Angular gradient polar plot
phi = np.linspace(-np.pi, np.pi, 300)
r_val = np.clip((phi + np.pi) / (2 * np.pi), 0, 1)
g_val = np.clip(1.0 - (phi + np.pi) / (2 * np.pi), 0, 1)

ax2_polar = fig.add_subplot(122, projection='polar')
ax2.set_visible(False)
colors_rgb = np.column_stack([r_val, g_val, np.full_like(r_val, 0.3)])
for i in range(len(phi) - 1):
    ax2_polar.fill_between([phi[i], phi[i+1]], 0, 1,
                           color=colors_rgb[i], alpha=0.9)
ax2_polar.set_title('Angular Color Gradient (phic)', pad=15)
ax2_polar.set_yticks([])

plt.tight_layout()
_guide_images = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "source", "guides", "images"))
plot_path = os.path.join(_guide_images, "06_cylindrical_plot.png")
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.show()
