from pathlib import Path

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

# Execution controls
render = True
export = True

# Rectangular comparison block (mm)
block_size_x = 100.0
block_size_y = 10.0
block_size_z = 100.0

# Fuzzy-skin parameter ranges (mm)
fuzzy_skin_thickness_min = 0.0
fuzzy_skin_thickness_max = 1.0
fuzzy_skin_point_distance_min = 0.5
fuzzy_skin_point_distance_max = 1.5

# PrusaSlicer project export
compiler_voxel_size = 0.15
num_regions = 10
output_directory_name = "output"
output_filename = f"fuzzy_skin_rect_prism_{num_regions}x{num_regions}.3mf"

# Center the block in X and Y, with its base on Z = 0.
block_min_x = -0.5 * block_size_x
block_min_z = 0.0
block_center = pv.Vec3(0.0, 0.0, 0.5 * block_size_z)
block_size = pv.Vec3(block_size_x, block_size_y, block_size_z)

x_normalized_expr = (
    f"clamp((x - ({block_min_x})) / ({block_size_x}), 0, 1)"
)
z_normalized_expr = (
    f"clamp((z - ({block_min_z})) / ({block_size_z}), 0, 1)"
)

fuzzy_skin_thickness_expr = (
    f"{fuzzy_skin_thickness_min} + "
    f"({fuzzy_skin_thickness_max} - {fuzzy_skin_thickness_min}) * "
    f"{z_normalized_expr}"
)
fuzzy_skin_point_distance_expr = (
    f"{fuzzy_skin_point_distance_min} + "
    f"({fuzzy_skin_point_distance_max} - {fuzzy_skin_point_distance_min}) * "
    f"{x_normalized_expr}"
)

block = pv.RectPrism(block_center, block_size)
block.set_attribute(
    pv.DefaultAttributes.FUZZY_SKIN_THICKNESS,
    pv.FloatAttribute(fuzzy_skin_thickness_expr),
)
block.set_attribute(
    pv.DefaultAttributes.FUZZY_SKIN_POINT_DISTANCE,
    pv.FloatAttribute(fuzzy_skin_point_distance_expr),
)

root = block

if render:
    viz.Render(root)

if export:
    here = Path(__file__).resolve().parent
    output_dir = here / output_directory_name
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / output_filename

    compiler = pvc.PrusaSlicerProjectCompiler(
        root,
        pv.Vec3(
            compiler_voxel_size,
            compiler_voxel_size,
            compiler_voxel_size,
        ),
        str(output_path),
        num_regions,
    )

    def report_progress(progress):
        print(f"Slicer export progress: {progress * 100:.1f}%")

    compiler.set_progress_callback(report_progress)
    compiler.compile()
    print("Wrote", output_path)
    print("Enable fuzzy skin for Outside walls when opening the project in PrusaSlicer.")
