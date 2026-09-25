"""Import solver-neutral TET4 result arrays as ordinary OpenVCAD attributes."""

import numpy as np
import pyvcad as pv


points = np.array(
    [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 1.0, 1.0],
    ],
    dtype=np.float64,
)
cells = np.array([[0, 1, 2, 3], [1, 2, 3, 4]], dtype=np.int64)

temperature = 20.0 + 2.0 * points[:, 0] + 3.0 * points[:, 1] + points[:, 2]
displacement = np.column_stack(
    (0.1 * points[:, 0], -0.05 * points[:, 1], 0.2 * points[:, 2])
)
material_zone = np.array([10.0, 20.0], dtype=np.float64)

results = pv.UnstructuredFieldDataset.from_tetrahedra(points, cells)
results.add_point_scalar(
    "temperature",
    temperature,
    units="degC",
    step_identifier="load-1",
    description="Analytic point scalar for the public array-import example",
)
results.add_point_vector(
    "displacement",
    displacement,
    units="mm",
    step_identifier="load-1",
)
results.add_cell_scalar(
    "material_zone",
    material_zone,
    description="Discontinuous cell-associated identifier",
)

print("Domain: {} points, {} TET4 cells".format(
    results.domain.point_count, results.domain.cell_count
))
print("Fields:")
for field_name in results.field_names:
    metadata = results.field_metadata(field_name)
    association = (
        "point" if metadata.association == pv.FieldAssociation.POINT else "cell"
    )
    print(
        "  {}: association={}, components={}, values={}, range={}..{}, units={!r}".format(
            metadata.name,
            association,
            metadata.component_count,
            metadata.value_count,
            metadata.minimum,
            metadata.maximum,
            metadata.units,
        )
    )

temperature_attribute = results.float_attribute("temperature")
displacement_attribute = results.vec3_attribute("displacement")
zone_attribute = results.float_attribute("material_zone")

known_points = np.vstack((points[cells[0]].mean(axis=0), points[cells[1]].mean(axis=0)))
print("Known interior samples:")
for point in known_points:
    vector = displacement_attribute.sample(*point, 0.0)
    print(
        "  p={} temperature={:.3f} displacement=({:.4f}, {:.4f}, {:.4f}) zone={:.1f}".format(
            point.tolist(),
            temperature_attribute.sample(*point, 0.0),
            vector.x,
            vector.y,
            vector.z,
            zone_attribute.sample(*point, 0.0),
        )
    )

coverage_points = np.vstack(
    (
        known_points,
        np.array([[-0.02, 0.0, 0.0], [-0.20, 0.0, 0.0]], dtype=np.float64),
    )
)
coverage = results.coverage(
    coverage_points,
    outside="boundary_clamp",
    max_distance=0.05,
)
print(
    "Coverage: total={} inside={} tolerance_adjusted={} clamped={} outside={} "
    "max_clamp_distance={:.6f}".format(
        coverage.total_queries,
        coverage.inside_count,
        coverage.tolerance_adjusted_count,
        coverage.boundary_clamped_count,
        coverage.outside_count,
        coverage.maximum_clamp_distance,
    )
)
for failure in coverage.representative_failures:
    print(
        "  outside p=({}, {}, {}) boundary_distance={:.6f}".format(
            failure.position.x,
            failure.position.y,
            failure.position.z,
            failure.boundary_distance,
        )
    )

