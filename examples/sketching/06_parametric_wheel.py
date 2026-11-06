import pyvcad as pv
import pyvcad_rendering as viz

# A parametric spoked wheel: every feature comes from these numbers, so a loop or an if statement is
# all it takes to make a family of wheels.
spokes = 5
rim_radius = 40.0
rim_width = 6.0
hub_radius = 10.0
bore_radius = 4.0
spoke_root = 9.0     # spoke width at the hub
spoke_tip = 5.0      # spoke width at the rim
thickness = 8.0

# One spoke, sketched along +X: tapered sides joined by a tangent arc at the hub end.
inner = hub_radius - 2.0
outer = rim_radius - rim_width + 2.0
spoke = pv.Sketch((inner, -spoke_root / 2))
spoke.line_to(outer, -spoke_tip / 2).line_to(outer, spoke_tip / 2).line_to(inner, spoke_root / 2)
spoke.tangent_arc_to(inner, -spoke_root / 2)
spoke = spoke.close().profile()

# The rim and hub, the spokes turned around the axis, and webs where they meet.
wheel = (pv.Profile.circle(rim_radius) - pv.Profile.circle(rim_radius - rim_width)) | pv.Profile.circle(hub_radius)
for i in range(spokes):
    wheel = wheel | spoke.rotated(360.0 * i / spokes)
wheel = wheel.round_concave(3.0)

# A keyed bore: a circle with a flat, made from a boolean and filleted where the flat meets the arc.
bore = (pv.Profile.circle(bore_radius) & pv.Profile.rectangle(2 * bore_radius, 1.7 * bore_radius, center=(0.0, -0.15 * bore_radius)))
viz.plot_profile(wheel - bore.fillet(0.8))

# A crowned wheel: the offset law pushes every edge of the section out by 1 mm at mid-thickness.
part = pv.Extrude(wheel, thickness, symmetric=True, offset_law=[(0.0, 0.0), (0.5, 1.0), (1.0, 0.0)])

# A hub boss revolved from a half-section on the XZ plane (x is the radius, y the height).
boss_section = pv.Profile.polygon([(bore_radius, -thickness), (hub_radius + 2.0, -thickness / 2),
                                   (hub_radius + 2.0, thickness / 2), (bore_radius, thickness)])
hub = pv.Revolve(boss_section.round_convex(1.0))

# Grade both from a stiff hub to a softer rim. The revolve's "u" coordinate is the distance from the
# axis, and like every coordinate field it is defined everywhere, so the spokes can use it too.
radial = hub.coordinate_field("u").map_range(hub_radius, rim_radius, 1000.0, 200.0, clamp=True)
part.set_attribute(pv.DefaultAttributes.MODULUS, radial)
hub.set_attribute(pv.DefaultAttributes.MODULUS, radial)

# Cut the keyed bore through everything last, so the crown cannot close it.
root = pv.Difference(pv.Union(part, hub), pv.Extrude(bore.fillet(0.8), 3 * thickness, symmetric=True))

viz.Render(root)
