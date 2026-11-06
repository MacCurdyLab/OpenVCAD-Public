"""Geometry grading: thicken gyroid walls around a mounting boss with a distance ramp."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

BOSS_CENTER = (12.0, 0.0, 0.0)  # mm
BOSS_RADIUS = 6.0               # mm
HOLE_RADIUS = 3.0               # mm
RAMP_DISTANCE = 12.0            # mm, walls are back to normal this far from the boss
NEAR_WALL = 1.4                 # mm, wall thickness against the boss
FAR_WALL = 0.5                  # mm, wall thickness away from the boss

cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-36.0, -18.0, -6.0), pv.Vec3(36.0, 18.0, 6.0)), cell_size=6.0
)
boss = pv.Cylinder(pv.Vec3(*BOSS_CENTER), BOSS_RADIUS, 12.0)

# mm.distance_field gives the distance to any node in mm; the ramp turns it into 0 at the
# boss and 1 from RAMP_DISTANCE on, clamped, so the wall stays within the two values.
near_boss = mm.ramp(
    0.0, RAMP_DISTANCE, coordinates=mm.distance_field(boss, bandwidth=RAMP_DISTANCE + 6.0)
)
wall_thickness = near_boss.map_range(0.0, 1.0, NEAR_WALL, FAR_WALL)

lattice = pv.Difference(mm.gyroid(cell_map, wall_thickness=wall_thickness), boss)
boss_with_hole = pv.Difference(boss, pv.Cylinder(pv.Vec3(*BOSS_CENTER), HOLE_RADIUS, 14.0))
root = pv.Union(lattice, boss_with_hole)
viz.Render(root)
