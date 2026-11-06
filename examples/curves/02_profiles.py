import pyvcad as pv
import pyvcad_rendering as viz

# A bracket plate: a rounded rectangle with two bolt holes and a slot cut out.
plate = pv.Profile.rounded_rectangle(40.0, 24.0, 4.0)
plate = plate - pv.Profile.circle(3.0, center=(-12, 5)) - pv.Profile.circle(3.0, center=(12, 5))
plate = plate - pv.Profile.slot(18.0, 5.0, center=(0, -5))

# Booleans keep the exact curves: a keyhole from a circle and a rectangle. fillet() rounds the
# corners between straight edges with exact arcs.
keyhole = pv.Profile.circle(8.0, center=(0, 4)) | pv.Profile.rectangle(8.0, 20.0, center=(0, -6))
keyhole = keyhole.fillet(2.0)

# Offsets and fillets: a hexagon with rounded corners, and a 2 mm wall around it.
hexagon = pv.Profile.regular_polygon(6, 12.0).fillet(3.0)
wall = hexagon.offset(2.0) - hexagon

# Thin slabs to look at the profiles (Extrude places a profile's plane at z = 0).
root = pv.Union([
    pv.Translate(-50, 0, 0, pv.Extrude(plate, 2.0)),
    pv.Extrude(keyhole, 2.0),
    pv.Translate(45, 0, 0, pv.Extrude(wall, 2.0)),
])

viz.Render(root)
