"""
Importing a build that mixes a solid and a lattice.

The spinal implant sample is a complete part: one object is the solid ALIF cage
body, and a second object is an 11,821-beam lattice that fills its windows. Both
appear as build items, so importing the whole build unions them, exactly as the
specification requires a consumer to do.

Pass object_id to bring in one object on its own. That is the quickest way to
work with the lattice separately, for example to give it its own material while
the solid body keeps another.
"""
from pathlib import Path

import pyvcad as pv
import pyvcad_rendering as viz

example_dir = Path(__file__).resolve().parent
model_path = example_dir.parent.parent / "data" / "beam_lattice" / "spinal_implant.3mf"

# mesh_voxel_size sets the voxel size used for the solid body's signed distance
# field. The cage has fine surface teeth, so it is worth resolving finely.
part = pv.ThreeMFBeamLattice(str(model_path), mesh_voxel_size=0.2)

for imported in part.imported_objects:
    kind = f"{len(imported.beams)} beams" if imported.has_lattice else f"{len(imported.triangles)} triangles"
    print(f"object {imported.object_id}: {imported.name} ({kind})")

# Either object can be imported on its own.
lattice_only = pv.ThreeMFBeamLattice(str(model_path), object_id=2)
print(f"lattice alone: {lattice_only.beam_count} beams")

root = part

viz.Render(root)
