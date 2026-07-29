import pyvcad as pv
import pyvcad_rendering as viz

# 1. Define geometry: A box centered at origin
box = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 4, 4))

# 2. Rotate it by 90 degrees
rotated_box = pv.Rotate(0.0, 0.0, 90.0, box)

# 3. Create Identity Node as parent of rotated box
identity = pv.Identity(rotated_box)

# 4. Color the box dynamically using a Color Map based on actual X world position.
# The gradient is based on global X position from -10 to +10.
r_expr = "clamp((x + 10.0) / 20.0, 0.0, 1.0)"
b_expr = "1.0 - clamp((x + 10.0) / 20.0, 0.0, 1.0)"
color_attr = pv.Vec4Attribute(
    r_expr,
    "0.0",
    b_expr,
    "1.0"
)

# We assign to Identity so it evaluates in global coordinate space since Identity 
# evaluates attributes before passing unrotated coords to children components.
identity.set_attribute(pv.DefaultAttributes.COLOR_RGBA, color_attr)

viz.Render(identity)
