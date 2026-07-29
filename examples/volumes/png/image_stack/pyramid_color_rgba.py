import os

import pyvcad as pv
import pyvcad_rendering as viz


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STACK_DIR = os.path.join(SCRIPT_DIR, "pyramid_stack")

# The stack is generated once and committed as deterministic source data.
voxel_size = pv.Vec3(0.35, 0.35, 0.35)

png_loader = pv.PNGLoader.FromStack(
    STACK_DIR,
    voxel_size,
    pv.PNGColorMode.COLOR_RGBA,
    center=True,
)
color_volume = png_loader.as_rgba_volume()

carrier_min, carrier_max = color_volume.bounding_box()
carrier = pv.RectPrism.FromMinAndMax(carrier_min, carrier_max)
carrier.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(color_volume))

root = carrier

viz.Render(root)
