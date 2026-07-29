"""Place cubic and BCC beam lattices on opposite sides of one shared map."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


# The shared map makes the cubic and BCC cell boundaries line up.
cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -12.0, -8.0), pv.Vec3(24.0, 12.0, 8.0)),
    cells=(6, 3, 2),
)

# Build each beam network across the complete map before keeping one half.
cubic = mm.cubic(cell_map, beam_radius=0.58, node_radius=0.78)
bcc = mm.bcc(cell_map, beam_radius=0.52, node_radius=0.78)

left_region = pv.RectPrism.FromMinAndMax(
    pv.Vec3(-30.0, -18.0, -12.0),
    pv.Vec3(0.0, 18.0, 12.0),
)
right_region = pv.RectPrism.FromMinAndMax(
    pv.Vec3(0.0, -18.0, -12.0),
    pv.Vec3(30.0, 18.0, 12.0),
)
# The two box regions meet at x = 0, making an intentionally sharp topology change.
root = pv.Union(
    pv.Intersection(cubic, left_region),
    pv.Intersection(bcc, right_region),
)
viz.Render(root)
