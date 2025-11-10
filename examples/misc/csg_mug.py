import pyvcad as pv
import pyvcad_rendering as viz

# Define materials
materials = pv.default_materials
blue = materials.id('blue')
green = materials.id('green')

# Cup Outside
rect_prism = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(2.1, 2.1, 2.9), blue)
cup_function = pv.Function('x^2 + y^2 - 1^2', blue)
cup_outside = pv.Intersection()
cup_outside.add_child(rect_prism)
cup_outside.add_child(cup_function)

# Handle
handle_function = pv.Function('(x^2 + y^2 + z^2 + 1.15^2 - 0.5^2)^2 - 4 * (1.15) * (x^2 + y^2)', green)
handle_scale = pv.Scale(0.85, 0.85, 0.85, handle_function)
handle_rotate = pv.Rotate(90, 0, 0, pv.Vec3(0,0,0), handle_scale)
handle_translate = pv.Translate(1, 0, 0, handle_rotate)

# Union of Cup Outside and Handle
cup_and_handle = pv.Union()
cup_and_handle.add_child(cup_outside)
cup_and_handle.add_child(handle_translate)

# Inside of Cup
inside_rect_prism = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(2.1, 2.1, 2.9), blue)
inside_function = pv.Function('x^2 + y^2 - 1^2', blue)
inside_intersection = pv.Intersection()
inside_intersection.add_child(inside_rect_prism)
inside_intersection.add_child(inside_function)

inside_scale = pv.Scale(0.75, 0.75, 1.0, inside_intersection)
inside_translate = pv.Translate(0, 0, 0.25, inside_scale)

# Difference to create the final mug
mug = pv.Difference()
mug.set_left(cup_and_handle)
mug.set_right(inside_translate)

root = mug

viz.Render(root, materials)