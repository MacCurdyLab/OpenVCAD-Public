import pyvcad as pv
import pyvcad_rendering as viz

# 1. An offset law shapes the walls along the height: (fraction of the height, outward offset) points,
#    joined smoothly. Here a fluted vase swells, pinches at the neck and flares at the lip, and twists.
flutes = 8
flute = pv.Profile.circle(4.0, center=(11.0, 0.0))
section = pv.Profile.circle(12.0)
for i in range(flutes):
    section = section | flute.rotated(360.0 * i / flutes)
vase = pv.Extrude(section.round_concave(1.5), 60.0, twist=45.0, offset_law=[(0.0, 0.0), (0.35, 5.0), (0.75, -1.5), (1.0, 2.0)])
vase.set_attribute(pv.DefaultAttributes.MODULUS,
                   vase.coordinate_field("normalized_height").map_range(0.0, 1.0, 200.0, 1000.0))

# 2. A loft blends between sections at chosen heights: here a round duct becomes a rounded rectangle
#    and then a smaller circle.
duct = pv.Loft([pv.Profile.circle(12.0), pv.Profile.rounded_rectangle(30.0, 18.0, 4.0), pv.Profile.circle(7.0)],
               [0.0, 30.0, 60.0])
duct.set_attribute(pv.DefaultAttributes.MODULUS,
                   duct.coordinate_field("normalized_height").map_range(0.0, 1.0, 200.0, 1000.0))

# 3. Sections may differ in topology: one disc splits into two legs. smooth=False blends linearly
#    between neighbouring sections (the default passes smoothly through every section).
legs = pv.Profile.circle(5.0, center=(-7.0, 0.0)) | pv.Profile.circle(5.0, center=(7.0, 0.0))
split = pv.Loft([pv.Profile.circle(12.0), legs], [0.0, 60.0], smooth=False)
split.set_attribute(pv.DefaultAttributes.MODULUS,
                    split.coordinate_field("normalized_height").map_range(0.0, 1.0, 200.0, 1000.0))

root = pv.Union([pv.Translate(-50, 0, 0, vase), duct, pv.Translate(50, 0, 0, split)])

viz.Render(root)
