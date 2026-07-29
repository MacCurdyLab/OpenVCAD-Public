import pyvcad as pv
import pyvcad_rendering as viz

# Start with an attribute-less rectangular prism, long along X
prism = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 4, 4))

# Rotate the prism 90 degrees about Z FIRST
rotated_prism = pv.Rotate(0.0, 0.0, 90.0, prism)

# Wrap in Identity to apply gradient in GLOBAL coordinates.
# The Identity node does nothing geometrically — it simply acts as an
# empty container that we can attach attributes to.
root = pv.Identity(rotated_prism)

# Attach the same gradient — but now it stays aligned to the global X-axis!
color_gradient = pv.Vec4Attribute(
    "clamp((x + 10.0) / 20.0, 0.0, 1.0)",
    "0.0",
    "1.0 - clamp((x + 10.0) / 20.0, 0.0, 1.0)",
    "1.0"
)
root.set_attribute(pv.DefaultAttributes.COLOR_RGBA, color_gradient)

viz.Render(root, pv.default_materials)
