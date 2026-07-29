import os
import pyvcad as pv
import pyvcad_rendering as viz
import matplotlib.pyplot as plt
import numpy as np

# --- Parameters ---
side = 40.0
thickness = 10.0
half_side = side / 2.0

# Diagonal linear gradient: f(x, y) = (x + y) normalized to [0, 1]
diag_expr_r = f'clamp((x + y + {side}) / ({2 * side}), 0, 1)'
diag_expr_g = f'1.0 - clamp((x + y + {side}) / ({2 * side}), 0, 1)'
diag_expr_b = '0.3'
diag_expr_a = '1.0'

# Radial gradient in XY plane: distance from Z axis normalized to [0, 1]
max_rho = half_side * np.sqrt(2)
radial_expr = f'clamp(sqrt(x^2 + y^2) / {max_rho}, 0, 1)'

# Volume fractions: radial blend between two materials in XY
materials = pv.default_materials
vf_expr_a = f'clamp(sqrt(x^2 + y^2) / {half_side}, 0, 1)'
vf_expr_b = f'1.0 - clamp(sqrt(x^2 + y^2) / {half_side}, 0, 1)'

# --- Build Object ---
slab = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(side, side, thickness))

# Diagonal color gradient
color_attr = pv.Vec4Attribute(diag_expr_r, diag_expr_g, diag_expr_b, diag_expr_a)
slab.set_attribute(pv.DefaultAttributes.COLOR_RGBA, color_attr)

# Radial modulus
radial_attr = pv.FloatAttribute(radial_expr)
slab.set_attribute(pv.DefaultAttributes.MODULUS, radial_attr)

# Volume fractions (radial blend)
vf_attr = pv.VolumeFractionsAttribute([
    (vf_expr_a, materials.id("red")),
    (vf_expr_b, materials.id("blue"))
])
slab.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, vf_attr)

root = slab
viz.Render(root, materials)

# --- Matplotlib Plots ---
res = 200
xi = np.linspace(-half_side, half_side, res)
yi = np.linspace(-half_side, half_side, res)
X, Y = np.meshgrid(xi, yi)

# Diagonal gradient
diag_z = np.clip((X + Y + side) / (2 * side), 0, 1)

# Radial gradient
radial_z = np.clip(np.sqrt(X**2 + Y**2) / max_rho, 0, 1)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

im1 = ax1.imshow(diag_z, extent=[-half_side, half_side, -half_side, half_side],
                 origin='lower', cmap='RdYlGn_r')
ax1.set_xlabel('x (mm)')
ax1.set_ylabel('y (mm)')
ax1.set_title('Diagonal Gradient (x + y)')
plt.colorbar(im1, ax=ax1, label='Value')

im2 = ax2.imshow(radial_z, extent=[-half_side, half_side, -half_side, half_side],
                 origin='lower', cmap='viridis')
ax2.set_xlabel('x (mm)')
ax2.set_ylabel('y (mm)')
ax2.set_title('Radial Gradient (XY plane)')
plt.colorbar(im2, ax=ax2, label='Value')

plt.tight_layout()
_guide_images = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "source", "guides", "images"))
plot_path = os.path.join(_guide_images, "04_multiaxis_plot.png")
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.show()
