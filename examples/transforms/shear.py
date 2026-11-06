import numpy as np
import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# A hollow column standing on the plane z = 0
column = pv.Difference(pv.RectPrism(pv.Vec3(0, 0, 15), pv.Vec3(10, 10, 30)),
                       pv.Cylinder(pv.Vec3(0, 0, 15), 3.0, 32.0))

# Shear: points slide along +X by tan(25 degrees) times their height above the plane z = 0,
# so the base stays put and the column leans. The bore leans with it.
lean = np.tan(np.radians(25.0))
leaning = pv.Transform.shear(pv.Vec3(1, 0, 0), pv.Vec3(0, 0, 1), lean, column.clone())
leaning.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([("1.0", materials.id("red"))]))

# shear_matrix() returns the 4x4 matrix, so a shear composes with other matrices:
# here a sideways shear about the column's mid-height, then a move along -X.
T = np.eye(4)
T[:3, 3] = [-25.0, 0.0, 0.0]
S = pv.Transform.shear_matrix(pv.Vec3(0, 1, 0), pv.Vec3(0, 0, 1), -lean, origin=pv.Vec3(0, 0, 15))
side_lean = pv.Transform(T @ S, column.clone())
side_lean.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([("1.0", materials.id("green"))]))

column.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([("1.0", materials.id("blue"))]))
original = pv.Translate(-12.0, 0.0, 0.0, column)

root = pv.Union(0.0, [original, leaning, side_lean])

viz.Render(root, materials)
