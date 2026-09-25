"""
Importing a lattice-only 3MF beam lattice.

The 3MF Beam Lattice Extension stores a lattice as a list of beams indexed into
a mesh's vertex list, which is far more compact than tessellating every strut.
ThreeMFBeamLattice reads that file and rebuilds it as an implicit tree, so the
result is a live OpenVCAD node: it can be transformed, combined with other
geometry, given attributes, and compiled like anything else.

The pyramid sample is a lattice-only object. Its mesh carries no triangles at
all, which the extension explicitly permits, and 156 of its 391 beams declare a
different radius at each end so they taper along their length.
"""
from pathlib import Path

import pyvcad as pv
import pyvcad_rendering as viz

example_dir = Path(__file__).resolve().parent
model_path = example_dir.parent.parent / "data" / "beam_lattice" / "pyramid.3mf"

lattice = pv.ThreeMFBeamLattice(str(model_path))

# Everything the file declared is available for inspection after import.
imported = lattice.imported_objects[0]
tapered = sum(1 for beam in imported.beams if beam.r1 != beam.r2)
print(f"object: {imported.name}")
print(f"beams: {lattice.beam_count} ({tapered} tapered)")
print(f"vertices: {len(imported.vertices)}, triangles: {len(imported.triangles)}")
print(f"default radius: {imported.radius:.5f} mm, min length: {imported.min_length} mm")
print(f"cap mode: {imported.cap}")

root = lattice

viz.Render(root)
