"""
BBoxUnion Smooth Demo - Compare sharp and smooth BBoxUnion on a dense child set.

This example builds three large union nodes from the same sphere field:
one sharp BBoxUnion, one smooth BBoxUnion, and one smooth regular Union.
The three clusters are placed side-by-side so the effect of the k-factor
and the agreement between BBoxUnion and Union are easy to see in the viewer.

The script also prints a few sample evaluate() values at the gaps between
children to show how the smooth node fills and rounds those regions.

NOTE: Use the "High" or "Ultra" preset in the viewer to see the full effect.

Green Objects: Smooth Union with k = 0.5
Blue Objects: Smooth BBoxUnion with k = 0.5
Red Objects: Sharp BBoxUnion with k = 0.0
"""
import math

import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

ROWS = 6
COLS = 8
SPHERE_RADIUS = 2.2
X_SPACING = 4.7
Y_SPACING = 4.1
SMOOTH_K = 0.5
SCENE_OFFSET = 48.0


def build_union_cluster(center_x, material_id, smooth_k, union_kind):
    if union_kind == "bbox":
        if smooth_k > 0.0:
            cluster = pv.BBoxUnion(smooth_k)
        else:
            cluster = pv.BBoxUnion()
    else:
        if smooth_k > 0.0:
            cluster = pv.Union(smooth_k, False)
        else:
            cluster = pv.Union()

    positions = {}

    for row in range(ROWS):
        row_x_offset = 0.5 * X_SPACING if row % 2 else 0.0

        for col in range(COLS):
            x = center_x + (col - (COLS - 1) / 2.0) * X_SPACING + row_x_offset
            y = (row - (ROWS - 1) / 2.0) * Y_SPACING
            z = math.sin(col * 0.55) * 0.9 + math.cos(row * 0.85) * 0.6

            sphere = pv.Sphere(pv.Vec3(x, y, z), SPHERE_RADIUS, material_id)
            cluster.add_child(sphere)
            positions[(row, col)] = (x, y, z)

    return cluster, positions


def midpoint(a, b):
    return (
        (a[0] + b[0]) * 0.5,
        (a[1] + b[1]) * 0.5,
        (a[2] + b[2]) * 0.5,
    )


def print_gap_samples(name, cluster, positions):
    center_row = ROWS // 2
    center_col = COLS // 2

    left = positions[(center_row, center_col - 1)]
    right = positions[(center_row, center_col)]
    upper = positions[(center_row - 1, center_col)]

    horizontal_gap = midpoint(left, right)
    diagonal_gap = midpoint(right, upper)

    print(name)
    print("  child count:", ROWS * COLS)
    print("  horizontal gap sample:", cluster.evaluate(*horizontal_gap))
    print("  diagonal gap sample:", cluster.evaluate(*diagonal_gap))


def build_scene():
    sharp_bbox_union, sharp_positions = build_union_cluster(
        -SCENE_OFFSET, materials.id("red"), 0.0, "bbox"
    )
    smooth_bbox_union, smooth_positions = build_union_cluster(
        0.0, materials.id("blue"), SMOOTH_K, "bbox"
    )
    smooth_union, smooth_union_positions = build_union_cluster(
        +SCENE_OFFSET, materials.id("green"), SMOOTH_K, "union"
    )
    root = pv.Union(False, [sharp_bbox_union, smooth_bbox_union, smooth_union])

    return (
        root,
        sharp_bbox_union,
        smooth_bbox_union,
        smooth_union,
        sharp_positions,
        smooth_positions,
        smooth_union_positions,
    )

(
    root,
    sharp_bbox_union,
    smooth_bbox_union,
    smooth_union,
    sharp_positions,
    smooth_positions,
    smooth_union_positions,
) = build_scene()

print("BBoxUnion comparison demo")
print("  left cluster  : sharp BBoxUnion")
print("  center cluster: smooth BBoxUnion(k={})".format(SMOOTH_K))
print("  right cluster : smooth Union(k={})".format(SMOOTH_K))
print_gap_samples("Sharp cluster", sharp_bbox_union, sharp_positions)
print_gap_samples("Smooth BBoxUnion cluster", smooth_bbox_union, smooth_positions)
print_gap_samples("Smooth Union cluster", smooth_union, smooth_union_positions)

center_row = ROWS // 2
center_col = COLS // 2
smooth_bbox_gap = midpoint(
    smooth_positions[(center_row, center_col - 1)],
    smooth_positions[(center_row, center_col)],
)
smooth_union_gap = midpoint(
    smooth_union_positions[(center_row, center_col - 1)],
    smooth_union_positions[(center_row, center_col)],
)
print(
    "Smooth BBoxUnion vs Union horizontal gap difference:",
    abs(
        smooth_bbox_union.evaluate(*smooth_bbox_gap) -
        smooth_union.evaluate(*smooth_union_gap)
    ),
)

viz.Render(root, materials)
