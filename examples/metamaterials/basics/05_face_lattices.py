"""Compare common crystallographic plates and an auxetic wall honeycomb."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

spacing = 34.0
structures = []

simple_cubic_map = mm.rectangular_cell_map(
    (
        pv.Vec3(-spacing - 12.0, -12.0, -12.0),
        pv.Vec3(-spacing + 12.0, 12.0, 12.0),
    ),
    cells=(3, 3, 3),
)
structures.append(
    mm.simple_cubic_plate(simple_cubic_map, wall_thickness=0.7)
)

cubic_octet_map = mm.rectangular_cell_map(
    (
        pv.Vec3(-12.0, -12.0, -12.0),
        pv.Vec3(12.0, 12.0, 12.0),
    ),
    cells=(3, 3, 3),
)
structures.append(
    mm.cubic_octet_plate(
        cubic_octet_map,
        cubic_wall_thickness=0.75,
        octet_wall_thickness=0.55,
    )
)

reentrant_ratio = mm.reentrant_hex_prism_reference_aspect_ratio(
    angle_degrees=-30.0,
    rib_ratio=2.0,
)
reentrant_map = mm.rectangular_cell_map(
    (
        pv.Vec3(spacing - 12.0 * reentrant_ratio, -12.0, -12.0),
        pv.Vec3(spacing + 12.0 * reentrant_ratio, 12.0, 12.0),
    ),
    cells=(3, 3, 3),
)
structures.append(
    mm.reentrant_honeycomb(
        reentrant_map,
        wall_thickness=0.7,
        angle_degrees=-30.0,
        rib_ratio=2.0,
    )
)

root = pv.Union(0.0, structures)
viz.Render(root)
