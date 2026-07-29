"""Measure geometry and directional cross-section uniformity in a TPMS cell."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


bounds = (
    pv.Vec3(-10.0, -10.0, -10.0),
    pv.Vec3(10.0, 10.0, 10.0),
)
cell_map = mm.rectangular_cell_map(bounds, cells=(2, 2, 2))
root = mm.gyroid(cell_map, wall_thickness=1.2)

report = mm.properties.characterize(
    root,
    voxel_size=0.4,
    bounds=bounds,
    periodic_axes="xyz",
)
print(report)

for axis, profile in report.cross_sections.items():
    print(
        "{}: min={:.3f}, mean={:.3f}, max={:.3f}, CV={:.3f}".format(
            axis.upper(),
            profile.minimum_area_fraction,
            profile.mean_area_fraction,
            profile.maximum_area_fraction,
            profile.coefficient_of_variation,
        )
    )

viz.Render(root)
