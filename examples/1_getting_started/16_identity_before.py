import pyvcad as pv
import pyvcad_rendering as viz

# A rectangular prism, long along X
prism = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 4, 4))

# Attach a color gradient that fits the un-rotated X extent [-10, +10]
# Red on the left, Blue on the right
color_gradient = pv.Vec4Attribute(
    "clamp((x + 10.0) / 20.0, 0.0, 1.0)",
    "0.0",
    "1.0 - clamp((x + 10.0) / 20.0, 0.0, 1.0)",
    "1.0"
)
prism.set_attribute(pv.DefaultAttributes.COLOR_RGBA, color_gradient)

# Rotate the prism 90 degrees about Z
# The gradient rotates WITH the object (local coordinates)
root = pv.Rotate(0.0, 0.0, 90.0, prism)

viz.Render(root, pv.default_materials)
