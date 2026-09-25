"""
Clipping modes, side by side.

The 3MF Beam Lattice Extension lets a lattice be clipped against a separate mesh
object in one of three modes: "none" leaves it alone, "inside" keeps only the
material inside the clipping volume, and "outside" keeps only the material
outside it.

OpenVCAD realises those modes as ordinary implicit CSG, which is what
ThreeMFBeamLattice does when it imports a clipped file. Because the clip is CSG
rather than a pre-trimmed mesh, you can swap the clipping volume for any other
OpenVCAD node afterwards.

This example builds one lattice three times against the same sphere, so the
three modes sit next to each other. Compare it with Figure 2-1 of the
specification.
"""
import pyvcad as pv
import pyvcad_rendering as viz

extent = 15.0        # mm, half-width of the lattice block
divisions = 5        # cells per axis
radius = 0.7         # mm, beam radius
clip_radius = 11.0   # mm
spacing = 42.0       # mm between the three copies

# A regular grid of nodes, wired up along each axis.
step = (2.0 * extent) / divisions
vertices = []
index_of = {}
for i in range(divisions + 1):
    for j in range(divisions + 1):
        for k in range(divisions + 1):
            index_of[(i, j, k)] = len(vertices)
            vertices.append(
                pv.Vec3(-extent + i * step, -extent + j * step, -extent + k * step)
            )

beams = []
for (i, j, k), index in index_of.items():
    for neighbour in ((i + 1, j, k), (i, j + 1, k), (i, j, k + 1)):
        if neighbour in index_of:
            beams.append(pv.Beam(index, index_of[neighbour]))

lattice = pv.BeamLattice(vertices, beams, radius)


def clipped(mode):
    """Applies one clipping mode to a fresh copy of the lattice."""
    body = pv.BeamLattice(vertices, beams, radius)
    sphere = pv.Sphere(pv.Vec3(0.0, 0.0, 0.0), clip_radius)
    if mode == pv.ClipMode.Inside:
        return pv.Intersection(body, sphere)
    if mode == pv.ClipMode.Outside:
        return pv.Difference(body, sphere)
    return body


modes = [pv.ClipMode.None_, pv.ClipMode.Inside, pv.ClipMode.Outside]

root = None
for index, mode in enumerate(modes):
    placed = pv.Translate((index - 1) * spacing, 0.0, 0.0, clipped(mode))
    root = placed if root is None else pv.Union(root, placed)

print(f"lattice: {lattice.active_beam_count} beams over {len(vertices)} vertices")

viz.Render(root)
