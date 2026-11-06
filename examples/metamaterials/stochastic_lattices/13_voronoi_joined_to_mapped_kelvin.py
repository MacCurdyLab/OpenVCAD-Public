"""Join a Voronoi foam to a mapped Kelvin lattice on a tube through an overlap band."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

INNER_RADIUS = 20.0    # mm
OUTER_RADIUS = 32.0    # mm
HEIGHT = 48.0          # mm, the tube runs from z = -24 to z = 24
CELLS = (28, 8, 2)     # around, along and through the wall; about 6 mm cells
BEAM_THICKNESS = 0.9   # mm
OVERLAP = 3.0          # mm, half-width of the band where both structures exist
SEED = 2

cell_map = mm.cylindrical_cell_map(
    (0.0, 0.0, 0.0), INNER_RADIUS, OUTER_RADIUS, HEIGHT, cells=CELLS
)
host = pv.Difference(
    pv.Cylinder(pv.Vec3(0.0, 0.0, 0.0), OUTER_RADIUS, HEIGHT),
    pv.Cylinder(pv.Vec3(0.0, 0.0, 0.0), INNER_RADIUS, HEIGHT + 2.0),
)

# The upper half is a Kelvin strut lattice tiled through the map.
kelvin = mm.graph_lattice(cell_map, mm.voronoi_unit_cell("bcc"), beam_radius=0.5 * BEAM_THICKNESS)

# The lower half is a Voronoi foam. Its seeds slide onto the same map's BCC sites as they
# approach the join, so near the band its cells are (almost) the mapped Kelvin cells and
# the two networks meet node to node; the overlap band guarantees the join where the
# curved map makes the match approximate.
foam_side = pv.RectPrism.FromMinAndMax(pv.Vec3(-40.0, -40.0, -40.0), pv.Vec3(40.0, 40.0, 0.0))
foam_host = pv.Intersection(host, pv.Offset(OVERLAP + 1.0, foam_side))
foam_host.prepare(pv.Vec3(0.4, 0.4, 0.4), 1.0)
foam = mm.voronoi_transition(
    foam_host,
    mm.ramp(-18.0, -6.0, axis="z"),
    kind="bcc",
    cell_map=cell_map,
    beam_thickness=BEAM_THICKNESS,
    seed=SEED,
)

root = pv.Intersection(mm.overlap(foam, kelvin, foam_side, OVERLAP), host)
print(mm.check_connectivity(root, voxel_size=0.25))
viz.Render(root)
