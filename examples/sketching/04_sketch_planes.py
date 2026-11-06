import pyvcad as pv
import pyvcad_rendering as viz

# An angle bracket built from sketches on several planes, like features in a CAD part tree.
width = 60.0
depth = 40.0
thickness = 5.0

# Base plate on the XY plane, extruded up along +Z, with two bolt slots.
base_profile = pv.Profile.rounded_rectangle(width, depth, 4.0, center=(0.0, depth / 2))
for x in (-21.0, 21.0):
    base_profile = base_profile - pv.Profile.slot(12.0, 6.0, center=(x, 26.0), angle=90.0)
base = pv.Extrude(base_profile, thickness)

# Upright on the XZ plane: the profile's x is world X and its y is world Z. Plane.xz() faces -Y, so a
# negative height extrudes toward +Y, back over the base.
upright_sketch = pv.Sketch((-width / 2, 0))
upright_sketch.line_to(width / 2, 0).line_to(width / 2, 30).arc_through((0, 48), (-width / 2, 30)).close()
upright_profile = upright_sketch.profile() - pv.Profile.circle(8.0, center=(0.0, 30.0))
upright = pv.Extrude(upright_profile, -thickness, plane=pv.Plane.xz())

# Gussets on YZ planes at x = -13 and x = 13, between the slots and clear of the hole (profile x is
# world Y, y is world Z), extruded symmetrically so each is centred on its plane.
gusset_profile = pv.Profile.polygon([(thickness, thickness), (thickness + 22, thickness), (thickness, thickness + 22)])
gussets = [pv.Extrude(gusset_profile, 4.0, symmetric=True, plane=pv.Plane.yz(x)) for x in (-13.0, 13.0)]

# A boss around the upright's hole, revolved about the hole's axis. Revolve spins a profile about its
# plane's y axis, so this plane sits at the hole centre with normal +Z and x along -X, which makes its
# y axis (normal x x_axis) point along -Y, out of the front face. The profile's x is the radius.
boss_plane = pv.Plane((0.0, 0.0, 30.0), normal=(0, 0, 1), x_direction=(-1, 0, 0))
boss = pv.Revolve(pv.Profile.rectangle(4.0, 6.0, center=(10.0, 3.0)), plane=boss_plane)

root = pv.Union([base, upright, *gussets, boss])

viz.Render(root)
