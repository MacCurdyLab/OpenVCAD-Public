"""
Volumes from NumPy arrays: one scalar, one vector and one volume-fraction field.

Every field here is a plain NumPy array built on the same 3D grid, loaded with
FloatVolume.from_array / Vec3sVolume.from_array and attached to a cube. Swap the
synthetic arrays for any data you can read into NumPy (NetCDF, HDF5, MRC, FITS,
raw bricks, simulation output) and the rest of the script stays the same.
"""
import numpy as np
import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# One regular grid shared by every field: 96 samples across a 40 mm cube.
# Arrays are indexed array[i, j, k] -> (x, y, z), so build the axes with indexing="ij".
resolution = 96
size = 40.0
spacing = size / (resolution - 1)
axis = np.linspace(-size / 2.0, size / 2.0, resolution)
x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
r = np.sqrt(x * x + y * y + z * z)

# 1. Scalar field: a hot core cooling outward, in degrees C
temperature = 20.0 + 80.0 * np.exp(-(r / 9.0) ** 2)
temperature_volume = pv.FloatVolume.from_array(temperature, spacing, center=True)

# 2. Vector field: a swirl about Z with an updraft through the core, in mm/s.
# Vector arrays carry their components in a trailing axis of length 3.
envelope = np.exp(-(r / 12.0) ** 2)
velocity = np.stack([-y * envelope, x * envelope, 6.0 * envelope], axis=-1)
velocity_volume = pv.Vec3sVolume.from_array(velocity, spacing, center=True)

# 3. Volume fractions: one array per material, summing to 1 everywhere.
# Red fills the core and blends smoothly into blue between r = 8 mm and r = 16 mm.
t = np.clip((r - 8.0) / 8.0, 0.0, 1.0)
red_fraction = 1.0 - t * t * (3.0 - 2.0 * t)
blue_fraction = 1.0 - red_fraction
red_volume = pv.FloatVolume.from_array(red_fraction, spacing, center=True)
blue_volume = pv.FloatVolume.from_array(blue_fraction, spacing, center=True)

# center=True centres the whole array on the origin, so every volume shares the
# same placement and one cube covers them all.
bbox_min, bbox_max = temperature_volume.bounding_box()
cube = pv.RectPrism.FromMinAndMax(bbox_min, bbox_max)

cube.set_attribute(pv.DefaultAttributes.TEMPERATURE, pv.FloatAttribute(temperature_volume))
cube.set_attribute("velocity", pv.Vec3Attribute(velocity_volume))
cube.set_attribute("red_fraction", pv.FloatAttribute(red_volume))
cube.set_attribute("blue_fraction", pv.FloatAttribute(blue_volume))

# Volume fractions are a per-material map rather than a single number, so the
# two sampled scalars are combined into VOLUME_FRACTIONS with a converter.
fractions = pv.VolumeFractionsExpressionConverter(
    ["red_fraction", "blue_fraction"],
    [materials.id("red"), materials.id("blue")],
    ["red_fraction", "blue_fraction"],
)
root = pv.AttributeModifier(fractions, cube)

viz.Render(root, materials)
