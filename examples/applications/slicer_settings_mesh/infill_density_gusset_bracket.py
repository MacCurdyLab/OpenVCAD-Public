import math
from pathlib import Path

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

# Execution controls
render = True
export = True

# Clipped right-angle gusset profile (mm)
gusset_leg_length = 165.0
gusset_thickness = 6.0
corner_clip_size = 12.0

# Three-hole fastener pattern (mm)
hole_diameter = 6.6
corner_hole_x = 30.0
corner_hole_y = 30.0
x_leg_hole_x = 117.0
x_leg_hole_y = 27.0
y_leg_hole_x = 27.0
y_leg_hole_y = 117.0
reinforcement_radius = 26.0
boolean_tool_margin = 2.0

# Infill-density field (%)
reinforced_infill_density = 70.0
nominal_infill_density = 10.0
blend_radius = 13.0
blend_passes = 3
blend_grid_voxel_size = 0.4

# PrusaSlicer project export
compiler_voxel_size = 0.15
num_regions = 6
output_directory_name = "output"
output_filename = "infill_density_gusset_bracket.3mf"

# Clip each corner by the same distance measured along its adjoining edges.
diagonal_clip_offset = corner_clip_size / math.sqrt(2.0)

# Counterclockwise hexagon formed by clipping the three corners of a right triangle.
profile_vertices = [
    pv.Vec3(corner_clip_size, 0.0, 0.0),
    pv.Vec3(gusset_leg_length - corner_clip_size, 0.0, 0.0),
    pv.Vec3(
        gusset_leg_length - diagonal_clip_offset,
        diagonal_clip_offset,
        0.0,
    ),
    pv.Vec3(
        diagonal_clip_offset,
        gusset_leg_length - diagonal_clip_offset,
        0.0,
    ),
    pv.Vec3(0.0, gusset_leg_length - corner_clip_size, 0.0),
    pv.Vec3(0.0, corner_clip_size, 0.0),
]
gusset = pv.PolygonExtrude(profile_vertices, gusset_thickness, True)

hole_centers = [
    pv.Vec3(corner_hole_x, corner_hole_y, 0.0),
    pv.Vec3(x_leg_hole_x, x_leg_hole_y, 0.0),
    pv.Vec3(y_leg_hole_x, y_leg_hole_y, 0.0),
]
boolean_tool_height = gusset_thickness + 2.0 * boolean_tool_margin
holes = pv.BBoxUnion([
    pv.Cylinder(center, 0.5 * hole_diameter, boolean_tool_height)
    for center in hole_centers
])
reinforcement_tools = pv.BBoxUnion([
    pv.Cylinder(center, reinforcement_radius, boolean_tool_height)
    for center in hole_centers
])

gusset_with_holes = pv.Difference(gusset, holes)
reinforced_regions = pv.Intersection(gusset_with_holes, reinforcement_tools)

reinforced_regions.set_attribute(
    pv.DefaultAttributes.INFILL_DENSITY,
    pv.FloatAttribute(reinforced_infill_density),
)
gusset_with_holes.set_attribute(
    pv.DefaultAttributes.INFILL_DENSITY,
    pv.FloatAttribute(nominal_infill_density),
)

# Put the collars first so their value wins over the base bracket
discrete_root = pv.Union(reinforced_regions, gusset_with_holes)
root = pv.Blend(
    discrete_root,
    [pv.DefaultAttributes.INFILL_DENSITY],
    [blend_radius, blend_radius, blend_radius],
    num_passes=blend_passes,
    override_voxel_size=[
        blend_grid_voxel_size,
        blend_grid_voxel_size,
        blend_grid_voxel_size,
    ],
)

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
        region_overlap_mm=0.5
    )
    def report_progress(progress):
        print(f"Slicer export progress: {progress * 100}%")
    compiler.set_progress_callback(report_progress)
    compiler.compile()
    print("Wrote", output_path)
