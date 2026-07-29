"""
Demonstrates the TreeDiagram-centered Mermaid export workflow.

This example builds a small CSG assembly, attaches a few attributes so the
diagram includes attribute artifacts, saves the Mermaid source to disk,
renders an SVG through the Mermaid CLI, and then opens the OpenVCAD scene.
NOTE: you need to have the Mermaid CLI installed and available in your PATH for the SVG export to work. You can install it with npm:
    npm install -g @mermaid-js/mermaid-cli
"""

from pathlib import Path

import pyvcad as pv
import pyvcad_rendering as viz

# Cup outside: Intersection(RectPrism, Function)
rect_prism = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(2.1, 2.1, 2.9))
cup_function = pv.Function("x^2 + y^2 - 1^2")
cup_outside = pv.Intersection(rect_prism, cup_function)

# Handle: Function -> Scale -> Rotate -> Translate
handle_fn = pv.Function("(x^2 + y^2 + z^2 + 1.15^2 - 0.5^2)^2 - 4 * 1.15 * (x^2 + y^2)")
handle_scale = pv.Scale(0.85, handle_fn)
handle_rotate = pv.Rotate(90, 0, 0, handle_scale)
handle_translate = pv.Translate(1, 0, 0, handle_rotate)

# Union(cup_outside, handle_translate)
cup_and_handle = pv.Union(cup_outside, handle_translate)

# Cup inside: a directly authored smaller cylinder -> Translate
inside_rect = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(2.1 * 0.75, 2.1 * 0.75, 2.9))
inside_func = pv.Function("x^2 + y^2 - 0.75^2")
inside_intersect = pv.Intersection(inside_rect, inside_func)
inside_translate = pv.Translate(0, 0, 0.25, inside_intersect)

# Final mug: Difference(cup_and_handle, inside)
root = pv.Difference(cup_and_handle, inside_translate)

# Add attributes so the Mermaid diagram shows both active and overridden artifacts.
# The root color overrides the child colors, so those child COLOR_RGBA artifacts
# should still appear in the diagram but in the dimmed "ignored" style.
cup_outside.set_attribute(
    pv.DefaultAttributes.COLOR_RGBA,
    pv.Vec4Attribute(0.82, 0.84, 0.90, 1.0),
)
handle_translate.set_attribute(
    pv.DefaultAttributes.COLOR_RGBA,
    pv.Vec4Attribute(0.55, 0.34, 0.22, 1.0),
)
cup_and_handle.set_attribute(
    pv.DefaultAttributes.DENSITY,
    pv.FloatAttribute("1.0 + 0.08 * z"),
)
inside_translate.set_attribute(
    pv.DefaultAttributes.HU,
    pv.FloatAttribute(-350.0),
)
root.set_attribute(
    pv.DefaultAttributes.COLOR_RGBA,
    pv.Vec4Attribute(0.97, 0.97, 1.0, 1.0),
)

viz.Render_Tree_Diagram(root, "mug_tree_diagram.mmd")
viz.Render_Tree_Diagram(root, "mug_tree_diagram.svg")
viz.Render_Tree_Legend("openvcad_master_legend.mmd")
viz.Render_Tree_Legend("openvcad_master_legend.svg")

# You can also view the .mmd files here: https://mermaid.ai/live/edit

viz.Render(root)
