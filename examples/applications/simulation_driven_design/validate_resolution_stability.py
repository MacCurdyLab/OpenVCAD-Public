"""Run Study 1 at its two documented resolutions and compare verification metrics."""

import json

from cantilever_study import run_study
from study_common import ensure_output_directory, write_json


coarse = run_study(
    fast=True,
    render=False,
    output_name="validation_stability_coarse",
)
fine = run_study(
    fast=False,
    render=False,
    output_name="validation_stability_fine",
)


def relative_difference(first, second):
    scale = max(abs(first), abs(second), 1.0e-30)
    return abs(first - second) / scale


comparison = {
    "coarse_target_cell_size_mm": coarse["mesh"]["target_cell_size_mm"],
    "fine_target_cell_size_mm": fine["mesh"]["target_cell_size_mm"],
    "coarse_cell_count": coarse["mesh"]["cell_count"],
    "fine_cell_count": fine["mesh"]["cell_count"],
    "baseline_maximum_displacement_relative_difference": relative_difference(
        coarse["baseline"]["maximum_displacement_mm"],
        fine["baseline"]["maximum_displacement_mm"],
    ),
    "verification_maximum_displacement_relative_difference": relative_difference(
        coarse["verification"]["maximum_displacement_mm"],
        fine["verification"]["maximum_displacement_mm"],
    ),
    "verification_strain_energy_relative_difference": relative_difference(
        coarse["verification"]["strain_energy_mj"],
        fine["verification"]["strain_energy_mj"],
    ),
    "coarse_budget": coarse["allocation"][
        "achieved_volume_weighted_vero_fraction"
    ],
    "fine_budget": fine["allocation"][
        "achieved_volume_weighted_vero_fraction"
    ],
    "structural_solves": 4,
    "note": "Separate validation path; each main Study 1 command still performs exactly one baseline and one verification solve.",
}

maximum_allowed_relative_difference = 0.35
comparison["maximum_allowed_relative_difference"] = (
    maximum_allowed_relative_difference
)
comparison["passed"] = (
    comparison["verification_maximum_displacement_relative_difference"]
    <= maximum_allowed_relative_difference
    and comparison["verification_strain_energy_relative_difference"]
    <= maximum_allowed_relative_difference
)

output_directory = ensure_output_directory("validation_stability")
output_path = output_directory / "metrics.json"
write_json(output_path, comparison)
print(json.dumps(comparison, indent=2, sort_keys=True))
if not comparison["passed"]:
    raise RuntimeError("Study 1 verification solve failed the resolution-stability check")
