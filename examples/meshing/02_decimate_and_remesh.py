"""Lighten a dense voxel mesh by decimation, or even out its triangles by remeshing."""

import pyvcad as pv
import pyvcad_rendering as viz

VOXEL_SIZE = 0.2  # mm
TARGET_RATIO = 0.05  # keep about 5% of the triangles
MAX_ERROR = 0.02  # mm; never move the surface farther than about this
EDGE_LENGTH = 1.0  # mm; target edge length for remeshing

# A block and a sphere joined by a smooth (k = 2 mm) union: flat faces next to curved ones.
shape = pv.Union(2.0, [pv.RectPrism(pv.Vec3(-5, 0, 0), pv.Vec3(14, 10, 10)), pv.Sphere(pv.Vec3(6, 0, 0), 7.0)])
dense = pv.SurfaceMesh(shape, VOXEL_SIZE)

# Decimation collapses edges where the surface is flattest first, so curved regions keep more
# triangles. Both limits apply: it stops at the ratio or at the error bound, whichever comes first.
light = dense.decimated(target_ratio=TARGET_RATIO, max_error=MAX_ERROR)

# Remeshing redistributes vertices for near-equilateral triangles of one size, which suits
# flattening, simulation pre-processing and smooth shading.
even = dense.remeshed(EDGE_LENGTH, iterations=3)

for name, mesh in (("voxel mesh", dense), ("decimated", light), ("remeshed", even)):
    print(f"{name:>10}: {mesh.triangle_count:>8,} triangles, volume {mesh.volume:8.1f} mm^3, "
          f"closed {mesh.is_closed()}")

root = pv.Mesh(light)
viz.Render(root)
