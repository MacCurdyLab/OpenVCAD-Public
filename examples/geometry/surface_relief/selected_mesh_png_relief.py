"""Add a repeating PNG relief to an explicitly selected imported-mesh patch."""

from pathlib import Path

import pyvcad as pv
import pyvcad_rendering as viz


data = Path(__file__).resolve().parents[2] / "data"
mesh_path = data / "3d_models" / "domed_tile.stl"
height_map_path = data / "height_maps" / "dotted_checker.png"

# Select the top of the tile by its triangle IDs.
source_mesh = pv.SurfaceMesh(str(mesh_path))
patch = pv.TriangleMeshSurface.from_selection(
    source_mesh,
    list(range(450)),
    u_axis_hint=pv.Vec3(1, 0, 0),
)

height = pv.ImageHeightField(
    str(height_map_path),
    amplitude_mm=1.2,
    channel="luminance",
    mapping="repeat",
    repeats=(5, 5),
)
relief = pv.SurfaceReliefVolume(
    patch,
    height,
    embed_mm=0.4,
    edge_falloff_mm=1.5,
)

# Join the relief to the original tile to make one printable part.
solid = pv.Mesh(source_mesh, override_voxel_size=0.2)
root = pv.BBoxUnion([solid, relief])

viz.Render(root)
