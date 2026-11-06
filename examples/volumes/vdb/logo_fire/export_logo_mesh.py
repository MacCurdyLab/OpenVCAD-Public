"""
Export the OpenVCAD logo V (examples/logo/openvcad_logo.py) as a watertight STL for the Blender bake.

The logo script is run with its interactive render stripped, its SDF is sampled with
pv.TreeSampler and contoured at zero with VTK flying edges. The mesh stays in the logo's own
frame: Y up, front face toward +Z, millimetres. Run it with the repo .venv:

    python export_logo_mesh.py logo_v.stl 0.5

The second argument is the sampling voxel size in mm (0.5 gives ~70k triangles, plenty for a
Mantaflow emitter and much faster to voxelise each frame than a finer mesh).
"""
import os
import sys

import numpy as np
import pyvcad as pv
from vtkmodules.util import numpy_support as vtk_np
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkFiltersCore import vtkCleanPolyData, vtkFeatureEdges, vtkFlyingEdges3D, vtkTriangleFilter
from vtkmodules.vtkIOGeometry import vtkSTLWriter

out_path = sys.argv[1] if len(sys.argv) > 1 else "logo_v.stl"
h = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

# Build the logo tree from its example script without opening the viewer
logo_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "logo", "openvcad_logo.py")
source = open(logo_script).read().replace("import pyvcad_rendering as viz", "").replace("viz.Render(root)", "")
namespace = {}
exec(compile(source, logo_script, "exec"), namespace)
root = namespace["root"]

voxel = pv.Vec3(h, h, h)
root.prepare(voxel, 10.0)
sampler = pv.TreeSampler(root, voxel, None)
sdf = np.ascontiguousarray(sampler.as_signed_distance_array(None), dtype=np.float32)
nx, ny, nz = sampler.sample_dimensions()
bbox_min, bbox_max = root.bounding_box()

image = vtkImageData()
image.SetDimensions(nx, ny, nz)
image.SetSpacing(h, h, h)
image.SetOrigin(bbox_min.x - 2 * h, bbox_min.y - 2 * h, bbox_min.z - 2 * h)   # TreeSampler pads two voxels
image.GetPointData().SetScalars(vtk_np.numpy_to_vtk(sdf, deep=True))

contour = vtkFlyingEdges3D()
contour.SetInputData(image)
contour.SetValue(0, 0.0)
contour.ComputeNormalsOff()
triangles = vtkTriangleFilter()
triangles.SetInputConnection(contour.GetOutputPort())
clean = vtkCleanPolyData()
clean.SetInputConnection(triangles.GetOutputPort())
clean.Update()
mesh = clean.GetOutput()

# Watertight check: no boundary or non-manifold edges
edges = vtkFeatureEdges()
edges.SetInputData(mesh)
edges.BoundaryEdgesOn()
edges.NonManifoldEdgesOn()
edges.FeatureEdgesOff()
edges.ManifoldEdgesOff()
edges.Update()
print(f"{mesh.GetNumberOfPolys()} triangles, {edges.GetOutput().GetNumberOfCells()} open/non-manifold edges, bounds {mesh.GetBounds()}")

writer = vtkSTLWriter()
writer.SetFileName(out_path)
writer.SetInputData(mesh)
writer.SetFileTypeToBinary()
writer.Write()
print(f"wrote {out_path}")
