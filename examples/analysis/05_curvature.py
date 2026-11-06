"""Find sharp edges and tight bends with a curvature field."""

import pyvcad as pv
import pyvcad_rendering as viz

# An L-bracket: the inside corner has a 3 mm fillet, every other edge is sharp, and a 4 mm
# hole runs through the upright.
base = pv.RectPrism(pv.Vec3(0.0, 0.0, 2.0), pv.Vec3(30.0, 20.0, 4.0))
upright = pv.RectPrism(pv.Vec3(-13.0, 0.0, 12.0), pv.Vec3(4.0, 20.0, 24.0))
bracket = pv.Union([base, upright], blend_radius=3.0, profile=pv.BlendProfile.circular)
hole = pv.Rotate(0.0, 90.0, 0.0, pv.Cylinder(pv.Vec3(-13.0, 0.0, 16.0), 2.0, 10.0))
part = pv.Difference(bracket, hole)

# "maximum" is 1 / the tightest bend radius at each point, in 1/mm: 0 on flat faces, 1/3 on the
# 3 mm fillet, 1/2 around the hole, and about 1 / step (here 10) on sharp edges, where a fillet
# may be needed.
bend = pv.FloatAttribute.curvature(part, "maximum", voxel_size=0.2, bandwidth=2.0)
part.set_attribute("curvature", bend)

viz.Render(part)
