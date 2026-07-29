import pyvcad as pv
import pyvcad_rendering as viz

# Red on the left, green on the right, blended in a 2mm-wide band across the shared face.
attribute = pv.DefaultAttributes.COLOR_RGBA

left_box = pv.RectPrism.FromMinAndMax(pv.Vec3(-15.0, -15.0, -15.0), pv.Vec3(0.0, 15.0, 15.0))
left_box.set_attribute(attribute, pv.Vec4Attribute(1.0, 0.0, 0.0, 1.0))
right_box = pv.RectPrism.FromMinAndMax(pv.Vec3(0.0, -15.0, -15.0), pv.Vec3(15.0, 15.0, 15.0))
right_box.set_attribute(attribute, pv.Vec4Attribute(0.0, 1.0, 0.0, 1.0))
combined = pv.Union(left_box, right_box)

# num_passes=2 gives a slightly softer (tent-like) ramp; set to 1 for a pure linear ramp.
smoothed = pv.Blend(combined, [attribute], [5.0, 5.0, 5.0], num_passes=2, override_voxel_size=[0.25,0.25,0.25])

viz.Render(smoothed)
