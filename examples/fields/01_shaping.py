import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

# One ramp along x: 0 at x = -30 and 1 at x = +30.
ramp = pv.FloatAttribute("x").normalize(-30.0, 30.0)

# Four shapes of the same ramp, one per bar (front to back):
# linear, smootherstep (flat at both ends), power 3 (starts slowly),
# and a smooth transfer curve that rises quickly and then holds a plateau.
weights = [
    ramp.ease("linear"),
    ramp.ease("smootherstep"),
    ramp.ease("power", 3.0),
    ramp.transfer([(0.0, 0.0), (0.3, 0.8), (0.7, 0.8), (1.0, 1.0)], interpolation="smooth"),
]

bars = pv.Union()
for row, weight in enumerate(weights):
    bar = pv.RectPrism(pv.Vec3(0, 14 * row, 0), pv.Vec3(60, 10, 4))
    # The shaped field is the red fraction; the rest of the bar is blue.
    bar.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,
                      pv.VolumeFractionsAttribute([(weight, red), (1.0 - weight, blue)]))
    bars.add_child(bar)

viz.Render(bars, materials)
