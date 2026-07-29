import os
import pyvcad as pv
import pyvcad_rendering as viz
import matplotlib.pyplot as plt
import numpy as np

# --- Parameters ---
radius = 15.0

# Skin effect: high stiffness at surface (d=0), decays into interior (d<0)
skin_thickness = 3.0
skin_min = 1.0
skin_max = 10.0
skin_expr = f'{skin_min} + ({skin_max} - {skin_min}) * exp(d / {skin_thickness})'

# Hard shell color: color the outer shell red, interior blue
# d <= 0 inside, d = 0 surface, d > 0 outside (but we only sample inside)
shell_thickness = 2.0
shell_r = f'clamp(1.0 + d / {shell_thickness}, 0, 1)'
shell_g = '0.1'
shell_b = f'clamp(-d / {shell_thickness}, 0, 1)'
shell_a = '1.0'

# Volume fractions: stiff skin material + soft core material
materials = pv.default_materials
vf_skin = f'clamp(1.0 + d / {skin_thickness}, 0, 1)'
vf_core = f'1.0 - clamp(1.0 + d / {skin_thickness}, 0, 1)'

# --- Build Object ---
sphere = pv.Sphere(pv.Vec3(0, 0, 0), radius)

# Skin modulus gradient
sphere.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(skin_expr))

# Shell color gradient
color_attr = pv.Vec4Attribute(shell_r, shell_g, shell_b, shell_a)
sphere.set_attribute(pv.DefaultAttributes.COLOR_RGBA, color_attr)

# Volume fractions
vf_attr = pv.VolumeFractionsAttribute([
    (vf_skin, materials.id("red")),
    (vf_core, materials.id("blue"))
])
sphere.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, vf_attr)

root = sphere
viz.Render(root, materials)

# --- Matplotlib Plot ---
d = np.linspace(-10, 1, 300)

skin_y = skin_min + (skin_max - skin_min) * np.exp(d / skin_thickness)
shell_r_y = np.clip(1.0 + d / shell_thickness, 0, 1)
shell_b_y = np.clip(-d / shell_thickness, 0, 1)
vf_skin_y = np.clip(1.0 + d / skin_thickness, 0, 1)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)

ax1.plot(d, skin_y, label='Skin Modulus', linewidth=2, color='tab:orange')
ax1.axvline(0, color='gray', linestyle=':', alpha=0.7, label='Surface (d=0)')
ax1.set_ylabel('Modulus (MPa)')
ax1.set_title('Signed-Distance Gradients')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(d, shell_r_y, label='Red (skin)', linewidth=2, color='red')
ax2.plot(d, shell_b_y, label='Blue (core)', linewidth=2, color='blue')
ax2.plot(d, vf_skin_y, label='Skin VF', linewidth=2, color='tab:green', linestyle='--')
ax2.axvline(0, color='gray', linestyle=':', alpha=0.7)
ax2.set_xlabel('Signed Distance d (mm)')
ax2.set_ylabel('Value [0–1]')
ax2.set_title('Shell Color & Volume Fraction vs Distance')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
_guide_images = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "source", "guides", "images"))
plot_path = os.path.join(_guide_images, "05_signed_distance_plot.png")
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.show()
