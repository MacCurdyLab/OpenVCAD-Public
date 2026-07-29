import pyvcad as pv
import pyvcad_rendering as viz

# Two adjacent cubes sharing the X=0 face. Each carries a different density value (a scalar
# attribute). The pv.Blend node smooths the sharp attribute transition over a user-specified
# physical radius without touching geometry, and is a no-op elsewhere in the scene.
attribute = pv.DefaultAttributes.DENSITY

left_box = pv.RectPrism.FromMinAndMax(pv.Vec3(-15.0, -15.0, -15.0), pv.Vec3(0.0, 15.0, 15.0))
left_box.set_attribute(attribute, pv.FloatAttribute(0.0))
right_box = pv.RectPrism.FromMinAndMax(pv.Vec3(0.0, -15.0, -15.0), pv.Vec3(15.0, 15.0, 15.0))
right_box.set_attribute(attribute, pv.FloatAttribute(1.0))
combined = pv.Union(left_box, right_box)

# physical_radius controls the transition width (mm). Unlike Convolve, Blend precomputes the
# blurred attribute grid once in prepare() so sample() is O(1) regardless of radius.
smoothed = pv.Blend(combined, [attribute], [5.0, 5.0, 5.0], num_passes=2, override_voxel_size=[0.25,0.25,0.25])

viz.Render(smoothed)
