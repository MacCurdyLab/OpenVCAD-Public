import os

import pyvcad as pv
import pyvcad_rendering as viz


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOLUME_PATH = os.path.join(SCRIPT_DIR, "basic_density.vdb")

# Load the scalar density field from the VDB file and wrap it as an attribute.
density_volume = pv.vdb_loader.load_float_volume(VOLUME_PATH, "density", center=True)
density_attribute = pv.FloatAttribute(density_volume)

# Use the volume bounds to build a simple carrier cube for the sampled field.
volume_bbox_min, volume_bbox_max = density_volume.bounding_box()
cube = pv.RectPrism.FromMinAndMax(volume_bbox_min, volume_bbox_max)
cube.set_attribute(pv.DefaultAttributes.DENSITY, density_attribute)

root = cube

viz.Render(root)
