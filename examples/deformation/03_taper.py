import pyvcad as pv
import pyvcad_rendering as viz

# A square column, 20 x 20 x 60 mm, standing on the plane z = 0, with a grid of holes through it
column = pv.RectPrism(pv.Vec3(0, 0, 30), pv.Vec3(20, 20, 60))
holes = pv.Union(0.0, [pv.Rotate(0, 90, 0, pv.Cylinder(pv.Vec3(0, y, z), 2.5, 24.0))
                       for y in (-5, 5) for z in range(7, 60, 9)])
column = pv.Difference(column, holes)

# Taper along the z axis. The rate is the change in scale per millimetre, so the section is scaled
# by 1 - 0.01 * z about the axis: full size at the base, 40% at the top. Heights are unchanged.
tapered = pv.Warp.taper(-0.01, column, axis=pv.Vec3(0, 0, 1), origin=pv.Vec3(0, 0, 0))

# The scale is a coordinate field: grade stiffness with it.
tapered.set_attribute(pv.DefaultAttributes.MODULUS,
                      tapered.coordinate_field("scale").map_range(0.4, 1.0, 1000.0, 100.0))

viz.Render(tapered)
