"""
Round-trip an OpenVCAD tree through a coarse OpenVDB occupancy grid.

This example exports a normal OpenVCAD tree through the VDB compiler, then
loads the boolean occupancy grid back through SignedDistanceField with
different OpenVDB topology smoothing settings.
"""
from pathlib import Path

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz


EXAMPLE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = EXAMPLE_DIR / "output"
VDB_PATH = OUTPUT_DIR / "coarse_occupancy.vdb"

# First try (0.5,0.5,0.5), then try (0.1,0.1,0.1) observe what smoothing factor looked better at each
VOXEL_SIZE = pv.Vec3(0.5,0.5,0.5) # Export voxel size for the occupancy grid from the OpenVCAD implicit source
HALF_WIDTH_VOXELS = 3             # The half-width of the narrow band around the surface to compute SDF values for, in voxels. Does not affect the smoothing
CLOSING_STEPS = 0                 # The number of morphological closing steps to perform on the occupancy grid before computing the SDF. Closing can help fill small holes in the occupancy grid, but may also change the topology of the shape.
DILATION_VOXELS = 0               # The number of voxels to dilate the occupancy grid before computing the SDF. Dilation can help ensure the SDF fully encloses the original shape, but may also change the topology of the shape.
SMOOTHING_VARIANTS = [
    ("no smoothing", 0, pv.Vec4Attribute("1", "0", "0", "1.0")), # Red- no smoothing steps
    ("default smoothing", 3, pv.Vec4Attribute("0", "1", "0", "1.0")), # Green- default smoothing steps
    ("more smoothing", 8, pv.Vec4Attribute("0", "0", "1", "1.0")), # Blue- many smoothing steps
]
SPACING = 22.0
REPORTED_PROGRESS = set()
VOLUME_SAMPLE_SIZE = 0.1          # Uniform sample size used by Node.volume() for all reported volumes.

def make_source_shape():
    """Create the source tree that will be converted to occupancy voxels."""
    left_lobe = pv.Sphere(pv.Vec3(-3.0, 0.0, 0.0), 6.0)
    right_lobe = pv.Sphere(pv.Vec3(3.0, 0.0, 0.0), 6.0)
    bridge = pv.RectPrism(pv.Vec3(0.0, 0.0, 0.0), pv.Vec3(10.0, 5.0, 7.0))
    solid = pv.Union(pv.Union(left_lobe, right_lobe), bridge)

    vertical_hole = pv.Cylinder(pv.Vec3(0.0, 0.0, 0.0), 1.7, 16.0)
    horizontal_hole = pv.Rotate(
        0.0,
        90.0,
        0.0,
        pv.Cylinder(pv.Vec3(0.0, 0.0, 0.0), 1.35, 16.0),
    )
    holes = pv.Union(vertical_hole, horizontal_hole)
    return pv.Difference(solid, holes)


def colorize(node, color):
    node.set_attribute(pv.DefaultAttributes.COLOR_RGBA, color)
    return node


def report_volume(label, volume, reference_volume):
    loss = reference_volume - volume
    loss_percent = 100.0 * loss / reference_volume
    direction = "loss" if loss >= 0.0 else "gain"
    print(
        f"{label}: {volume:.2f} mm^3 "
        f"({abs(loss):.2f} mm^3 {direction}, {abs(loss_percent):.2f}% {direction} vs original)"
    )


def print_progress(percent):
    if percent in (0, 25, 50, 75, 100) and percent not in REPORTED_PROGRESS:
        REPORTED_PROGRESS.add(percent)
        print(f"vdb export: {percent}%")


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

source_for_export = make_source_shape()
original_volume = source_for_export.volume(VOLUME_SAMPLE_SIZE)
print(f"original design: {original_volume:.2f} mm^3")

compiler = pvc.VdbCompiler(
    source_for_export,
    VOXEL_SIZE,
    str(VDB_PATH),
    attributes_to_export=None,
    include_occupancy=True,
)
compiler.set_progress_callback(lambda p: print_progress(int(round(100.0 * p))))
compiler.compile()
print(f"wrote VDB file with surface and occupancy grids: {VDB_PATH}")

original = colorize(
    make_source_shape(),
    pv.Vec4Attribute("0.88", "0.88", "0.82", "1.0"),
)

comparison_nodes = [pv.Translate(-1.5 * SPACING, 0.0, 0.0, original)]

for index, (label, smoothing_steps, color) in enumerate(SMOOTHING_VARIANTS):
    # The topology settings below affect BoolGrid occupancy inputs only.
    # If this path pointed at a FloatGrid SDF, SignedDistanceField would load
    # it directly and ignore these topology conversion parameters.
    sdf = pv.SignedDistanceField(
        str(VDB_PATH),
        "occupancy",
        half_width_voxels=HALF_WIDTH_VOXELS,
        closing_steps=CLOSING_STEPS,
        dilation_voxels=DILATION_VOXELS,
        smoothing_steps=smoothing_steps,
    )
    report_volume(label, sdf.volume(VOLUME_SAMPLE_SIZE), original_volume)
    colorize(sdf, color)
    comparison_nodes.append(
        pv.Translate((-0.5 + index) * SPACING, 0.0, 0.0, sdf)
    )
    print(f"loaded {label}: smoothing_steps={smoothing_steps}")

root = pv.BBoxUnion(comparison_nodes)

viz.Render(root, pv.default_materials)
