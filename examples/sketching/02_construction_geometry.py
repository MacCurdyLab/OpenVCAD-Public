import pyvcad as pv
import pyvcad_rendering as viz

# A link plate around two bosses. In a CAD sketcher you would make the sides tangent to both bosses
# and dimension the holes; here each of those is one function call.
big_center, big_radius = (0.0, 0.0), 20.0
small_center, small_radius = (60.0, 0.0), 10.0

# The outer tangent lines of the two boss circles: the upper one first, then the lower one.
(upper_big, upper_small), (lower_big, lower_small) = pv.tangent_lines(big_center, big_radius, small_center, small_radius)[:2]

# Draw the outline counter-clockwise: along the lower tangent, around the small boss, back along the
# upper tangent and around the big boss. Each arc passes through the boss's far point.
s = pv.Sketch(lower_big)
s.line_to(*lower_small)
s.arc_through((small_center[0] + small_radius, 0.0), upper_small)
s.line_to(*upper_big)
s.arc_through((big_center[0] - big_radius, 0.0), lower_big)
s.close()
link = s.profile()

# Bores in the bosses.
link = link - pv.Profile.circle(10.0, center=big_center) - pv.Profile.circle(4.0, center=small_center)

# Two holes placed by distances, like dimensions in a CAD sketch: 26 from the big boss's centre and
# 40 from the small one's. The two circles of those radii meet at the hole centres.
for hole in pv.intersect_circles(big_center, 26.0, small_center, 40.0):
    link = link - pv.Profile.circle(2.5, center=hole)

# A lightening slot between the bosses.
link = link - pv.Profile.slot(16.0, 8.0, center=(36.0, 0.0))

viz.plot_profile(link)

# Stiffer near the edges, softer inside: the extrusion's profile_distance is the distance to the outline.
part = pv.Extrude(link, 6.0)
part.set_attribute(pv.DefaultAttributes.MODULUS,
                   part.coordinate_field("profile_distance").map_range(-6.0, 0.0, 200.0, 1000.0, clamp=True))

viz.Render(part)
