import numpy as np
import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

# Twenty "sensor readings" scattered over a plate, as NumPy arrays: positions in mm and one value
# each. In practice these come from measurements or a simulation exported as points.
rng = np.random.default_rng(7)
sensors = np.column_stack([rng.uniform(-40, 40, 20), rng.uniform(-25, 25, 20), np.zeros(20)])
readings = np.sin(sensors[:, 0] / 15.0) + 0.5 * np.cos(sensors[:, 1] / 10.0)

# A smooth field through every reading. "rbf" fits a thin-plate spline; "idw" averages the nearest
# readings and "nearest" copies the closest one. The field is defined everywhere, not just on the plate.
field = pv.FloatAttribute.from_points(sensors, readings, method="rbf")

# Map the readings' range onto a red fraction for display.
red_fraction = field.map_range(readings.min(), readings.max(), 0.0, 1.0, clamp=True)
plate = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(90, 60, 4))
plate.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,
                    pv.VolumeFractionsAttribute([(red_fraction, red), (1.0 - red_fraction, blue)]))

# Gray beads resting on the plate mark where the readings were taken.
beads = pv.Union(0.0, [pv.Sphere(pv.Vec3(x, y, 3.5), 1.5) for x, y, _ in sensors])
beads.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([("1.0", materials.id("gray"))]))

viz.Render(pv.Union(plate, beads), materials)
