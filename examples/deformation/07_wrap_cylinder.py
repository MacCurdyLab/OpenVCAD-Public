import math

import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
radius = 20.0

# A flat label: raised text on a thin band, authored in the plane z = 0 with z pointing out of the label.
# x runs along the circumference (0 to 2 pi r), y along the cylinder's axis.
circumference = 2.0 * math.pi * radius
band = pv.RectPrism(pv.Vec3(circumference / 2, 0, 0.5), pv.Vec3(circumference, 14, 1))
# pv.Text lays its glyphs out turned 180 degrees in the XY plane, so turn them upright first.
text = pv.Translate(circumference / 2, 0, 2.0, pv.Rotate(0, 0, 180, pv.Text("OpenVCAD", 9.0, 2.0)))
label = pv.Union(band, text)
label.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([("1.0", materials.id("red"))]))

# Wrap the label around a cylinder of radius 20 about the z axis. The seam (x = 0) faces +y, so the
# middle of the label (x = pi r) faces -y. Lengths on the surface are kept, and z = 0 lies on it.
wrapped = pv.Warp.wrap_cylinder(radius, label, center=pv.Vec3(0, 0, 0), axis=pv.Vec3(0, 0, 1),
                                reference_direction=pv.Vec3(0, 1, 0))

core = pv.Cylinder(pv.Vec3(0, 0, 0), radius, 30.0)
core.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([("1.0", materials.id("blue"))]))
root = pv.Union(core, wrapped)

viz.Render(root, materials)
