import pyvcad as pv
import pyvcad_rendering as viz

# Extrude: a plate with holes, graded from soft at the bottom to stiff at the top.
plate = pv.Profile.rounded_rectangle(36.0, 24.0, 4.0)
plate = plate - pv.Profile.circle(4.0, center=(-9, 0)) - pv.Profile.slot(12.0, 5.0, center=(8, 0), angle=90.0)
block = pv.Extrude(plate, 8.0)
block.set_attribute(pv.DefaultAttributes.MODULUS,
                    block.coordinate_field("normalized_height").map_range(0.0, 1.0, 100.0, 1000.0))

# Draft and twist: a hexagonal column that narrows by 4 degrees and turns 90 degrees as it rises,
# graded across its section; the section coordinate u turns with the twist.
hexagon = pv.Profile.regular_polygon(6, 9.0).fillet(1.5)
column = pv.Extrude(hexagon, 36.0, draft=4.0, twist=90.0)
column.set_attribute(pv.DefaultAttributes.MODULUS,
                     column.coordinate_field("u").map_range(-9.0, 9.0, 100.0, 1000.0))

# Revolve: a cup from a half-section (x is the distance from the axis), swept 270 degrees to show its
# wall, graded around the axis.
cup_profile = pv.Profile.polygon([(0, 0), (12, 0), (15, 20), (13.5, 20), (10.5, 2), (0, 2)])
cup = pv.Revolve(cup_profile, 270.0)
cup.set_attribute(pv.DefaultAttributes.MODULUS,
                  cup.coordinate_field("normalized_angle").map_range(0.0, 1.0, 100.0, 1000.0))

root = pv.Union([pv.Translate(-45, 0, 0, block), column, pv.Translate(45, 0, 0, cup)])

viz.Render(root)
