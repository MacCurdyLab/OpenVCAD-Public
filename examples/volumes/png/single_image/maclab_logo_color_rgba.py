import os

import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_compilers as pvc

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(SCRIPT_DIR, "MACLab_no_gradients_transparent_background.png")

# Each pixel becomes a voxel cell in x/y, and the single image is repeated
# through z until depth_mm is reached.
image_voxel_size = pv.Vec3(0.075, 0.075, 0.075)
depth_mm = 15.0

png_loader = pv.PNGLoader.FromImage(
    IMAGE_PATH,
    image_voxel_size,
    depth_mm,
    pv.PNGColorMode.COLOR_RGBA,
    center=True,
)
color_volume = png_loader.as_rgba_volume()

carrier_min, carrier_max = color_volume.bounding_box()
carrier = pv.RectPrism.FromMinAndMax(carrier_min, carrier_max)
carrier.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(color_volume))

root = carrier

viz.Render(root)
