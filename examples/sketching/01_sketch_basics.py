import pyvcad as pv
import pyvcad_rendering as viz

# Dimensions drive the sketch: change one and the whole outline follows.
length = 60.0
height = 12.0
tab_width = 20.0
corner_radius = 4.0

# The outline is drawn like a pen moving from point to point. fillet= and chamfer= treat the corner
# at the end of that piece; tangent_arc_to() continues the last piece without a kink, so the tab gets
# a half-round top.
s = pv.Sketch((0, 0))
s.line_to(length, 0, chamfer=3)
s.line_to(length, height + 8)
s.tangent_arc_to(length - tab_width, height + 8)
s.line_to(length - tab_width, height, fillet=3)
s.line_to(0, height, fillet=2)
s.close(fillet=corner_radius)

# A loop drawn inside the outline becomes a hole: two arcs make the round hole in the tab.
tab_center = (length - tab_width / 2, height + 8)
s.move_to(tab_center[0] - 4, tab_center[1])
s.arc_through((tab_center[0], tab_center[1] + 4), (tab_center[0] + 4, tab_center[1]))
s.arc_through((tab_center[0], tab_center[1] - 4), (tab_center[0] - 4, tab_center[1]))
s.close()

# Plain Python places features: a row of mounting holes.
plate = s.profile()
for i in range(3):
    plate = plate - pv.Profile.circle(2.0, center=(8 + 10 * i, height / 2))

# Check the sketch before building anything: holes are dashed, arrows show each loop's direction,
# and circles mark the corners.
viz.plot_profile(plate)

# Then turn it into a part, graded from soft at the left end to stiff at the tab.
part = pv.Extrude(plate, 4.0)
part.set_attribute(pv.DefaultAttributes.MODULUS, part.coordinate_field("u").map_range(0.0, length, 200.0, 1000.0))

viz.Render(part)
