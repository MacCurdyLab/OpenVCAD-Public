"""
Volume Demo - Estimate the volume of a simple sphere.

This example computes a sphere volume with the default automatic sample size,
then repeats the estimate at progressively higher manual resolutions before
opening the interactive renderer.
"""
import math

import pyvcad as pv
import pyvcad_rendering as viz

radius = 10.0  # mm
root = pv.Sphere(pv.Vec3(0.0, 0.0, 0.0), radius)

# For comparison, the exact volume of a sphere is (4 / 3) * pi * r^3.
actual_volume_mm3 = (4.0 / 3.0) * math.pi * radius**3
print(f"actual sphere volume: {actual_volume_mm3:.3f} mm^3")

# volume() approximates volume by sampling the signed distance field on a voxel
# grid. Smaller voxel sizes use a higher resolution and are generally more
# accurate, but they also take longer to compute.
volume_mm3 = root.volume()
print(f"default voxel size: {volume_mm3:.3f} mm^3")

for voxel_size_mm in [1.0, 0.5, 0.25]:
    volume_mm3 = root.volume(voxel_size_mm)
    print(f"{voxel_size_mm:.2f} mm voxel size: {volume_mm3:.3f} mm^3")

viz.Render(root)
