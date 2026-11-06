"""
ThreeMFBeamLattice Demo - Import a lattice saved with the 3MF Beam Lattice Extension.

ThreeMFBeamLattice reads the beams, radii, cap modes and balls declared in a
3MF file and rebuilds them as an implicit node that can be transformed,
combined, graded and compiled like any other.

See examples/lattices/beam_lattice/ for clipped and mesh-plus-lattice files.
"""
from pathlib import Path

import pyvcad as pv
import pyvcad_rendering as viz

model_path = Path(__file__).resolve().parents[1] / "data" / "beam_lattice" / "pyramid.3mf"

lattice = pv.ThreeMFBeamLattice(str(model_path))
print(f"beams: {lattice.beam_count}")

root = lattice

viz.Render(root)
