from pathlib import Path

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

# Execution controls
render = True
export = True

# Bar geometry (mm). X carries the gradient; the clean graded face is -Y.
block_size_x = 50.0
block_size_y = 5.0
block_size_z = 25.0

# Fuzzy-skin thickness ramp (mm). One straight linear traverse across the bar,
# so every region in a given export is the same width: block_size_x / N.
fuzzy_skin_thickness_min = 0.0
fuzzy_skin_thickness_max = 1.0

# Fixed fuzzy-skin point distance (mm). Held constant across the whole sweep so
# the region count is the only thing that changes. This is NOT set as an
# OpenVCAD attribute: the compiler segments every settings-mesh attribute it
# finds, so a constant one would still multiply the band count by N. Set it by
# hand in the PrusaSlicer print profile instead.
fuzzy_skin_point_distance = 0.4

# Target printer scale. Used only for the printed sweep report.
nozzle_diameter = 0.4
layer_height = 0.2

# THE SWEPT VARIABLE: how many regions the compiler cuts the same gradient
# into. One project file is exported per step.
num_regions_min = 5
num_regions_max = 50
num_regions_steps = 10

# Label inset into the back face (+Y) so it never touches the graded front
# face at -Y. Depth is doubled and the text is centred on the face plane, so
# exactly label_inset_depth of it bites into the bar. The pocket floor comes
# out slightly wavy at low N - the compiler's band field mixes attribute units
# with millimetres, which perturbs surfaces by up to half a band step - so the
# inset is cut deeper than it needs to be to stay legible across the sweep.
label_height = 8.0
label_inset_depth = 0.8
label_font = "Arial"
label_center_z = 0.5 * block_size_z

# Sampling resolution. Isotropic because the label is a real 3D feature: X has
# to resolve the narrowest region, Z the glyph strokes, and Y the inset depth.
compiler_voxel_size = 0.15
output_directory_name = "output"

# Which model to open in the interactive viewer. The geometry is identical
# across the sweep apart from the label, so any step shows the same gradient.
render_num_regions = num_regions_max

# Center the bar in X and Y, with its base on Z = 0.
block_min_x = -0.5 * block_size_x
block_center = pv.Vec3(0.0, 0.0, 0.5 * block_size_z)
block_size = pv.Vec3(block_size_x, block_size_y, block_size_z)
label_plane_y = 0.5 * block_size_y

x_normalized_expr = f"clamp((x - ({block_min_x})) / ({block_size_x}), 0, 1)"
fuzzy_skin_thickness_expr = (
    f"{fuzzy_skin_thickness_min} + "
    f"({fuzzy_skin_thickness_max} - {fuzzy_skin_thickness_min}) * "
    f"{x_normalized_expr}"
)

# Evenly spaced region counts, inclusive of both ends.
region_counts = [
    int(round(num_regions_min
              + (num_regions_max - num_regions_min) * i / (num_regions_steps - 1)))
    for i in range(num_regions_steps)
]


def build_bar(num_regions):
    """Graded bar with an N label inset into its back face."""
    block = pv.RectPrism(block_center, block_size)
    block.set_attribute(
        pv.DefaultAttributes.FUZZY_SKIN_THICKNESS,
        pv.FloatAttribute(fuzzy_skin_thickness_expr),
    )

    # Text is authored in XY and extruded along Z, so a 90 degree pitch stands
    # it up on a Y face: local +Y becomes +Z and local +Z becomes -Y. VTK lays
    # the glyphs out readable from -Z, which that pitch carries round to +Y -
    # hence the label goes on the +Y face, not -Y, or it comes out mirrored.
    label = pv.Text(
        f"N={num_regions:02d}",
        label_height,
        2.0 * label_inset_depth,
        pv.FontAspect.Bold,
        label_font,
    )
    label = pv.Rotate(90.0, 0.0, 0.0, label)

    # Rotate pivots about the child's bounding-box center rather than the
    # origin, so place the label from its measured bounds instead of assuming
    # where the rotation left it.
    label.prepare(
        pv.Vec3(compiler_voxel_size, compiler_voxel_size, compiler_voxel_size),
        6.0 * compiler_voxel_size,
    )
    label_min, label_max = label.bounding_box()
    label = pv.Translate(
        -0.5 * (label_min.x + label_max.x),
        label_plane_y - 0.5 * (label_min.y + label_max.y),
        label_center_z - 0.5 * (label_min.z + label_max.z),
        label,
    )

    return pv.Difference(block, label)


# Sweep report: the region width each export is asking the slicer to reproduce.
print(f"Bar: {block_size_x} x {block_size_y} x {block_size_z} mm, "
      f"linear {fuzzy_skin_thickness_min} -> {fuzzy_skin_thickness_max} mm ramp")
print(f"Exporting {len(region_counts)} projects, N = {region_counts[0]} .. "
      f"{region_counts[-1]}")
print()
print(f"{'N':>4}  {'region':>8}  {'/nozzle':>8}  {'fuzz pts':>9}  {'/voxel':>7}")
for num_regions in region_counts:
    region_width = block_size_x / num_regions
    print(
        f"{num_regions:>4}  {region_width:8.3f}  "
        f"{region_width / nozzle_diameter:8.2f}  "
        f"{region_width / fuzzy_skin_point_distance:9.1f}  "
        f"{region_width / compiler_voxel_size:7.1f}"
    )
print()

if render:
    viz.Render(build_bar(render_num_regions))

if export:
    here = Path(__file__).resolve().parent
    output_dir = here / output_directory_name
    output_dir.mkdir(exist_ok=True)

    for num_regions in region_counts:
        output_path = output_dir / f"fuzzy_skin_region_count_N{num_regions:02d}.3mf"

        compiler = pvc.PrusaSlicerProjectCompiler(
            build_bar(num_regions),
            pv.Vec3(
                compiler_voxel_size,
                compiler_voxel_size,
                compiler_voxel_size,
            ),
            str(output_path),
            num_regions,
        )

        def report_progress(progress, label=num_regions):
            print(f"  N={label:02d} export progress: {progress * 100:.1f}%")

        compiler.set_progress_callback(report_progress)
        compiler.compile()
        print("Wrote", output_path)

    print()
    print(
        "In PrusaSlicer: enable fuzzy skin for Outside walls, set "
        f"fuzzy skin point distance to {fuzzy_skin_point_distance} mm, and use a "
        f"{nozzle_diameter} mm nozzle at {layer_height} mm layers."
    )
