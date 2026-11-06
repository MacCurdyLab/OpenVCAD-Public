import numpy as np
import pyvcad as pv
import pyvcad_rendering as viz

# Hydrogen 3d_z2 orbital (n=3, l=2, m=0), built in numpy and loaded with
# FloatVolume.from_array. Any dense scientific grid (NetCDF, HDF5, MRC, FITS,
# raw bricks) loads the same way once it is a numpy array.
resolution = 161            # voxels per side
half_extent = 22.0          # field half-width in Bohr radii
mm_per_bohr = 1.5           # print scale

# psi_320 is proportional to (3z^2 - r^2) * exp(-r / 3) in units of the Bohr radius.
# Index order is array[i, j, k] -> x, y, z, so build the axes with indexing="ij".
axis = np.linspace(-half_extent, half_extent, resolution)
x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
r = np.sqrt(x * x + y * y + z * z)
psi = (3.0 * z * z - r * r) * np.exp(-r / 3.0)

# Store the probability density |psi|^2 carrying the sign of psi, normalised to
# [-1, 1], so one field drives both the phase colour and the opacity. The two
# positive lobes peak at +1; the negative torus peaks at about -0.25.
signed_density = np.sign(psi) * psi * psi
signed_density /= np.abs(signed_density).max()

# Voxels within the tolerance of zero stay inactive, keeping the grid sparse.
# center=True puts the nucleus at the origin.
voxel_size = 2.0 * half_extent * mm_per_bohr / (resolution - 1)
volume = pv.FloatVolume.from_array(signed_density, voxel_size, tolerance=1e-4, center=True)
orbital_attribute = pv.FloatAttribute(volume)

bbox_min, bbox_max = volume.bounding_box()
block = pv.RectPrism.FromMinAndMax(bbox_min, bbox_max)
block.set_attribute("orbital", orbital_attribute)

# Negative phase in blue, positive phase in amber; alpha rises with density so
# the faint outer shell stays clear and the dense cores read solid.
orbital_color_map = [
    [-0.250, pv.Vec4(0.05, 0.20, 0.75, 0.95)],
    [-0.120, pv.Vec4(0.10, 0.40, 0.90, 0.70)],
    [-0.040, pv.Vec4(0.30, 0.65, 1.00, 0.30)],
    [-0.008, pv.Vec4(0.55, 0.85, 1.00, 0.04)],
    [-0.002, pv.Vec4(0.55, 0.85, 1.00, 0.00)],
    [ 0.002, pv.Vec4(1.00, 0.85, 0.50, 0.00)],
    [ 0.008, pv.Vec4(1.00, 0.85, 0.50, 0.04)],
    [ 0.040, pv.Vec4(1.00, 0.65, 0.20, 0.30)],
    [ 0.150, pv.Vec4(0.95, 0.45, 0.08, 0.65)],
    [ 0.450, pv.Vec4(0.85, 0.22, 0.04, 0.90)],
    [ 1.000, pv.Vec4(0.65, 0.08, 0.02, 1.00)],
]

entries = [pv.LookupTableEntry(value, color) for value, color in orbital_color_map]
converter = pv.LookupTableConverter(
    ["orbital"],
    [pv.DefaultAttributes.COLOR_RGBA],
    entries,
    pv.InterpolationMode.LINEAR,
)
root = pv.AttributeModifier(converter, block)

viz.Render(root)
