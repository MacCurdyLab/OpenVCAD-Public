import pyvcad as pv
import pyvcad_rendering as viz

# Curves from data that OpenVCAD already has: a path over a mesh, the border of a mesh selection,
# and the contour of a node. Each becomes a tube on a sphere of radius 2.5.
mesh_file = "../data/3d_models/sphere.stl"
mesh = pv.SurfaceMesh(mesh_file)
sphere = pv.Mesh(mesh_file)
sphere.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(100.0))

# 1. The shortest path along mesh edges between two vertices, as a curve.
start = mesh.nearest_vertex(pv.Vec3(-2.0, -1.2, -0.8))
end = mesh.nearest_vertex(pv.Vec3(1.2, -1.6, 1.4))
seam = pv.Tube(mesh.shortest_surface_path(start, end).to_curve(), 0.1)

# 2. The border of a selection: every triangle within 1.2 mm of the top vertex, along the surface.
top = mesh.nearest_vertex(pv.Vec3(0.0, 0.0, 2.5))
cap = mesh.select_by_geodesic_radius(top, 1.2)
ring = pv.Tube(cap.boundary_loops()[0], 0.1)

# 3. The contour of a node: the sphere's outline at z = -1.25, traced with marching squares.
contour = pv.Tube(pv.contour_curves(sphere, -1.25, 0.02)[0], 0.1)

for tube in (seam, ring, contour):
    tube.set_attribute(pv.DefaultAttributes.MODULUS, pv.FloatAttribute(1000.0))
root = pv.Union([sphere, seam, ring, contour])

viz.Render(root)
