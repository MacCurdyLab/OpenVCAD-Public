"""Tessellate a STEP model exactly, keeping which CAD face every triangle came from."""

from collections import Counter
from pathlib import Path

import pyvcad as pv
import pyvcad_rendering as viz

DEFLECTION = 0.05  # mm; largest gap between triangles and the true CAD surface
ANGULAR_DEFLECTION = 15.0  # degrees between neighbouring triangle normals on curved faces
EDGE_LENGTH = 1.5  # mm; target edge length for the evened-out copy

step_path = Path(__file__).resolve().parents[1] / "data" / "3d_models" / "bracket.step"
model = pv.CADModel.from_step(str(step_path))

# No voxels involved: OpenCASCADE triangulates each face, and shared edges are welded so the
# result is closed. triangle_labels holds the CAD face index of every triangle.
mesh = model.to_surface_mesh(deflection=DEFLECTION, angular_deflection=ANGULAR_DEFLECTION)
labels = mesh.triangle_labels
print(f"{len(model.faces)} CAD faces -> {mesh.triangle_count:,} triangles, closed {mesh.is_closed()}")
print("triangles on the five busiest faces:", Counter(labels).most_common(5))

# Face labels work as region boundaries for selections, e.g. grow from a point but stay on its face.
seed = mesh.nearest_triangle(pv.Vec3(0, 0, 100))
face_patch = mesh.select_linked_constrained(seed.triangle_id, triangle_regions=labels)
print(f"face {labels[seed.triangle_id]} has {face_patch.triangle_count} triangles, "
      f"area {face_patch.area:.1f} mm^2 (CAD: {model.face(labels[seed.triangle_id]).area:.1f})")

# CAD triangulations have long, thin triangles. Remeshing evens them out while keeping every face
# border in place and carrying the face labels along.
even = mesh.remeshed(EDGE_LENGTH, iterations=3)
print(f"remeshed: {even.triangle_count:,} triangles, {len(set(even.triangle_labels))} faces kept")

root = model.to_node()
viz.Render(root)
