"""Create physical waves from a normalized functional height field."""

from pathlib import Path

import pyvcad as pv
import pyvcad_rendering as viz


mesh_path = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "3d_models"
    / "domed_tile.stl"
)
source_mesh = pv.SurfaceMesh(str(mesh_path))
patch = pv.TriangleMeshSurface.from_selection(
    source_mesh,
    list(range(450)),
    u_axis_hint=pv.Vec3(1, 0, 0),
)

# Functional fields receive normalized patch coordinates as x=u and y=v. The expression result
# is clamped to [0, 1], then multiplied by amplitude_mm.
waves = pv.FunctionalHeightField(
    pv.FloatAttribute(
        "0.5 + 0.25*sin(10*pi*x) + 0.25*sin(8*pi*y)"
    ),
    amplitude_mm=1.4,
)
relief = pv.SurfaceReliefVolume(
    patch,
    waves,
    embed_mm=0.4,
    edge_falloff_mm=1.5,
)

solid = pv.Mesh(source_mesh, override_voxel_size=0.2)
unioned_root = pv.BBoxUnion([solid, relief])

# SurfaceReliefVolume is geometry on its own. Render unioned_root instead to attach it to the tile.
root = relief
viz.Render(root)
