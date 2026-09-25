"""Exercise a generated feedback bundle using only public pyvcad APIs."""

import argparse
from pathlib import Path

import numpy as np
import pyvcad as pv


repository_root = Path(__file__).resolve().parents[3]
default_xdmf = (
    repository_root
    / ".tmp"
    / "simulation_driven_design"
    / "study1_cantilever"
    / "cantilever_feedback_results.xdmf"
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--xdmf", type=Path, default=default_xdmf)
arguments = parser.parse_args()

dataset = pv.XDMFFieldLoader.load(str(arguments.xdmf))
print("Loaded:", arguments.xdmf)
print("Fields:")
for field_name in dataset.field_names:
    metadata = dataset.field_metadata(field_name)
    print(
        "  {}: association={}, components={}, values={}, units={!r}".format(
            field_name,
            metadata.association,
            metadata.component_count,
            metadata.value_count,
            metadata.units,
        )
    )

scalar_name = "projected_strain_energy_density"
vector_name = "baseline_displacement"
scalar_attribute = dataset.float_attribute(scalar_name)
vector_attribute = dataset.vec3_attribute(vector_name)

points = np.asarray(dataset.domain.points)
cells = np.asarray(dataset.domain.cells)
known_points = np.vstack(
    (
        points[cells[0]].mean(axis=0),
        points[cells[-1]].mean(axis=0),
        points[cells[len(cells) // 2]].mean(axis=0),
    )
)

print("Known interior samples:")
for point in known_points:
    scalar_value = scalar_attribute.sample(*point, 0.0)
    vector_value = vector_attribute.sample(*point, 0.0)
    print(
        "  p={} energy={:.9e} displacement=({:.9e}, {:.9e}, {:.9e})".format(
            point.tolist(),
            scalar_value,
            vector_value.x,
            vector_value.y,
            vector_value.z,
        )
    )

coverage = dataset.coverage(known_points, outside="error")
print(
    "Coverage: total={} inside={} tolerance_adjusted={} clamped={} outside={}".format(
        coverage.total_queries,
        coverage.inside_count,
        coverage.tolerance_adjusted_count,
        coverage.boundary_clamped_count,
        coverage.outside_count,
    )
)
if coverage.outside_count != 0:
    raise RuntimeError("Known loader-smoke points were not covered")
