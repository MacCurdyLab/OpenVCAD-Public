"""
Importing a clipped 3MF beam lattice.

A beam lattice may declare a clipping mode and a separate mesh object to clip
against. The variable voronoi sample uses clipping mode "inside", so only the
lattice material inside its 100 mm cube survives; the half-radius overhang where
beams terminate on a cube face is trimmed away.

ThreeMFBeamLattice realises that clip natively: the clipping mesh is loaded as
an ordinary Mesh node and intersected with the lattice, so the result stays an
editable implicit tree rather than a pre-trimmed mesh. Pass apply_clipping=False
to import the raw beams and see what the clip removes.

This sample also shows radius resolution in action. 813 of its 1291 beams
declare no radius and inherit the lattice default of 0.5 mm; the rest carry
their own, which is what makes the lattice variable.
"""
from pathlib import Path

import pyvcad as pv
import pyvcad_rendering as viz

example_dir = Path(__file__).resolve().parent
model_path = example_dir.parent.parent / "data" / "beam_lattice" / "variable_voronoi.3mf"

# mesh_voxel_size controls how finely the clipping mesh is voxelized. Match it
# to the smallest feature you need the clip to resolve.
lattice = pv.ThreeMFBeamLattice(str(model_path), mesh_voxel_size=0.25)

imported = lattice.imported_objects[0]
inherited = sum(1 for beam in imported.beams
                if beam.r1 == imported.radius and beam.r2 == imported.radius)
print(f"object: {imported.name}")
print(f"beams: {lattice.beam_count} ({inherited} inheriting the {imported.radius} mm default)")
print(f"clip mode: {imported.clip_mode}, clipping mesh id: {imported.clipping_mesh_id}")
print(f"clipping mesh: {len(imported.clip_vertices)} vertices, {len(imported.clip_triangles)} triangles")

root = lattice

viz.Render(root)
