"""Crop a closed mesh with a plane and a shaped cut-out, then close the openings again."""

import pyvcad as pv
import pyvcad_rendering as viz

VOXEL_SIZE = 0.5  # mm
CROP_HEIGHT = -15.0  # mm; keep everything above this plane
NOTCH_RADIUS = 9.0  # mm; radius of the side cut-out
NOTCH_HEIGHT = 5.0  # mm; height of the cut-out axis
BIG = 200.0  # mm; Function nodes are only defined inside their box, so make it cover the mesh

# A lumpy closed surface standing in for a scan: three spheres blended by a smooth union.
blob = pv.Union(6.0, [
    pv.Sphere(pv.Vec3(0, 0, 0), 40.0),
    pv.Sphere(pv.Vec3(0, 15, 10), 32.0),
    pv.Sphere(pv.Vec3(0, -12, -5), 30.0),
])
scan = pv.SurfaceMesh(blob, VOXEL_SIZE)
low, high = pv.Vec3(-BIG, -BIG, -BIG), pv.Vec3(BIG, BIG, BIG)

# A plane as a signed distance: negative (inside) above the crop height.
plane = pv.Function(f"-(z - ({CROP_HEIGHT}))", low, high)
cropped = scan.clipped(plane, keep="inside")

# Any node works as a cutter. This expression is a cylinder along x; keep the outside of it.
notch = pv.Function(f"sqrt(y*y + (z - {NOTCH_HEIGHT})^2) - {NOTCH_RADIUS}", low, high)
cut = cropped.clipped(notch, keep="outside")
print("open boundary loops after cutting:", cut.boundary_loop_count())

# Close the two round side openings with faired patches that blend into the surface, then cap the
# large flat crop opening without fairing so it stays flat.
patched = cut.filled_holes(max_hole_size=40.0, fair=True)
print("after filling the side openings:", patched.boundary_loop_count())
closed = patched.filled_holes(fair=False)
print("after capping the crop:", closed.boundary_loop_count(), "| closed:", closed.is_closed(),
      f"| volume {closed.volume:,.0f} mm^3")

root = pv.Mesh(closed)
viz.Render(root)
