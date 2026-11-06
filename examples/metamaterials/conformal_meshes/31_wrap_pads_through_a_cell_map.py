"""Design solid pads and a boss flat, then wrap them onto a curved lattice shell.

``mm.map_node(cell_map, node)`` evaluates any node in the map's own coordinates. With the
default ``space="physical"`` those coordinates are approximate millimetres: the flat child box
``child_bounds`` (here about 207 x 40 x 6 mm) is rolled around the cylinder. The pads and the
boss are ordinary flat primitives placed in that box; once wrapped they follow the shell and
are unioned with the gyroid as solid mounting regions.
"""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

# A cylindrical shell, r = 30..36 mm, 40 mm tall, 24 cells around and 6 along the axis.
cell_map = pv.CellMap.cylindrical(pv.Vec3(0, 0, 0), 30.0, 36.0, 40.0, (24, 6, 1))

# The flat child box that covers the whole map, in approximate millimetres.
lower, upper = pv.MappedNode(cell_map, pv.Sphere(pv.Vec3(0, 0, 0), 1.0)).child_bounds
length, height, thickness = upper.x, upper.y, upper.z
print(f"child box: {length:.1f} x {height:.1f} x {thickness:.1f} mm")

# Two rectangular pads and a round boss, authored flat. Z spans the shell thickness.
pad_a = pv.RectPrism(pv.Vec3(0.25 * length, 0.5 * height, 0.5 * thickness),
                     pv.Vec3(24.0, 14.0, thickness + 2.0))
pad_b = pv.RectPrism(pv.Vec3(0.75 * length, 0.5 * height, 0.5 * thickness),
                     pv.Vec3(24.0, 14.0, thickness + 2.0))
boss = pv.Cylinder(pv.Vec3(0.5 * length, 0.5 * height, 0.5 * thickness), 7.0, thickness + 2.0)
features = pv.Union(pv.Union(pad_a, pad_b), boss)

root = pv.Union(
    mm.gyroid(cell_map, wall_thickness=0.7),
    mm.map_node(cell_map, features),
)

viz.Render(root)
