import numpy as np
import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# An L-shaped part, so rotations and reflections are easy to read
leg = pv.RectPrism(pv.Vec3(5, 0, 0), pv.Vec3(10, 4, 4))
upright = pv.RectPrism(pv.Vec3(1, 4, 0), pv.Vec3(2, 6, 4))
part = pv.Union(leg, upright)

# Transform takes one 4x4 matrix written row by row: world = M @ [x, y, z, 1].
# M = T @ R @ S scales first, then rotates (about the origin, right-hand rule), then translates.
angle = np.radians(60.0)
S = np.diag([1.5, 1.5, 1.5, 1.0])
R = np.array([[np.cos(angle), -np.sin(angle), 0, 0],
              [np.sin(angle), np.cos(angle), 0, 0],
              [0, 0, 1, 0],
              [0, 0, 0, 1]])
T = np.eye(4)
T[:3, 3] = [25.0, 0.0, 0.0]
placed = pv.Transform(T @ R @ S, part.clone())
placed.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([("1.0", materials.id("blue"))]))

# A non-uniform scale is allowed, but it warps the signed distance field: the surface is exact,
# distances away from it are a first-order estimate.
stretched = pv.Translate(-20.0, 0.0, 0.0, pv.Scale(1.0, 2.0, 0.5, part.clone()))
stretched.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([("1.0", materials.id("green"))]))

part.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([("1.0", materials.id("red"))]))

root = pv.Union(0.0, [part, placed, stretched])

viz.Render(root, materials)
