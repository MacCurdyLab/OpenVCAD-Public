"""Export a lattice dome to STL and 3MF, first with uniform and then with adaptive meshing."""

import time
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

VOXEL_SIZE = 0.4  # mm; halving it roughly quadruples triangles, file size and meshing time
ADAPTIVITY = 0.05  # 0 keeps uniform triangles; 0.01-0.05 suits curved lattices (see the guide)
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

# A gyroid shell over a dome, 120 mm across and 12 mm thick, sealed by a rim at its edges.
cell_map = mm.spherical_cell_map(pv.Vec3(0, 0, 0), 48.0, 60.0, (10.0, 80.0), cells=(24, 6, 2))
lattice = mm.gyroid(cell_map, wall_thickness=0.8)
root = pv.Union(lattice, mm.rim(cell_map, width=1.5))

# SurfaceMesh samples the tree on a voxel grid and extracts its surface.
start = time.perf_counter()
uniform = pv.SurfaceMesh(root, VOXEL_SIZE)
print(f"uniform : {uniform.triangle_count:>10,} triangles in {time.perf_counter() - start:5.1f} s")

# Adaptive meshing keeps sharp detail at voxel resolution but merges triangles on flat and gently
# curved regions. The surface stays closed.
start = time.perf_counter()
adaptive = pv.SurfaceMesh(root, VOXEL_SIZE, adaptivity=ADAPTIVITY)
print(f"adaptive: {adaptive.triangle_count:>10,} triangles in {time.perf_counter() - start:5.1f} s")
print("adaptive mesh is closed:", adaptive.is_closed())

OUTPUT_DIR.mkdir(exist_ok=True)
adaptive.write_stl(str(OUTPUT_DIR / "lattice_dome.stl"))
adaptive.write_3mf(str(OUTPUT_DIR / "lattice_dome.3mf"))
for path in sorted(OUTPUT_DIR.glob("lattice_dome.*")):
    print(f"{path.name}: {path.stat().st_size / 1e6:.1f} MB")

viz.Render(root)
