import pyvcad as pv
import pyvcad_rendering as viz

# A wavy sheet given as an unsigned distance: |z - wave(x, y)|. It has no inside of its own.
sheet = pv.Function("abs(z - 2 * sin(x / 3) * cos(y / 3))", pv.Vec3(-15, -15, -6), pv.Vec3(15, 15, 6))

# Thicken turns the sheet into a plate whose thickness grows from 0.6 mm to 3 mm along x.
thickness = pv.FloatAttribute("1.8 + 0.08 * x").clamp(0.6, 3.0)
plate = pv.Thicken(pv.ScalarParameter(thickness, minimum=0.6, maximum=3.0, lipschitz=0.08), sheet)

# Trim the plate to a square so its edges are clean.
root = pv.Intersection(plate, pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(28, 28, 12)))

viz.Render(root)
