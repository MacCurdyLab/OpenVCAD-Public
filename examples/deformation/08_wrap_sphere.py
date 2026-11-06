import math

import pyvcad as pv
import pyvcad_rendering as viz

radius = 25.0

# A flat sheet of studs, authored in the plane z = 0: x is arc length along the equator, y along a
# meridian. Rows at y = -16, 0 and 16 mm sit at latitudes of about -37, 0 and 37 degrees.
spacing = 2.0 * math.pi * radius / 16
studs = pv.Union(0.0, [pv.Cylinder(pv.Vec3(i * spacing + spacing / 2, y, 1.5), 2.5, 3.0)
                       for i in range(16) for y in (-16.0, 0.0, 16.0)])

# Wrap the sheet onto a sphere of radius 25. Lengths along the equator and the meridians are kept;
# parallels shrink toward the poles, so the upper and lower studs are narrower around the sphere.
wrapped = pv.Warp.wrap_sphere(radius, studs)

root = pv.Union(pv.Sphere(pv.Vec3(0, 0, 0), radius), wrapped)

# Latitude is a coordinate field of the wrap: grade with it.
root.set_attribute(pv.DefaultAttributes.MODULUS,
                   wrapped.coordinate_field("latitude").map_range(-90.0, 90.0, 100.0, 1000.0))

viz.Render(root)
