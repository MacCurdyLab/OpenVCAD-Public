"""Place a Schwarz-P cell through an ideal spherical protective shell band."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


shell_center = pv.Vec3(0.0, 0.0, 0.0)
inner_radius = 20.0
outer_radius = 26.0

# U follows longitude, V runs south to north, and W crosses the shell wall.
cell_map = mm.spherical_cell_map(
    center=shell_center,
    inner_radius=inner_radius,
    outer_radius=outer_radius,
    latitude_bounds_degrees=(-62.0, 62.0),
    longitude_count=20,
    latitude_count=10,
    radial_cell_size=3.0,
    north_axis=pv.Vec3(0.0, 0.0, 1.0),
    reference_direction=pv.Vec3(1.0, 0.0, 0.0),
)

root = mm.schwarz_p(cell_map, wall_thickness=0.65)

viz.Render(root)
