import pyvcad as pv
import pyvcad_rendering as viz

cube = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(10, 10, 10))

# Scale a copy by 2x uniformly
# Syntax: pv.Scale(scale, child_node)
scaled_cube = pv.Scale(2.0, cube)

# Translate the scaled cube so both are visible side-by-side
moved_scaled = pv.Translate(20.0, 0.0, 0.0, scaled_cube)

# Union the original and scaled cube to see them both
root = pv.Union(cube, moved_scaled)

viz.Render(root)
