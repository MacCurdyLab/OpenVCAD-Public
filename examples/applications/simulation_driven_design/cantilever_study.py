"""Study 1 implementation: Agilus30/Vero cantilever feedback."""

import time

import numpy as np
import pyvcad as pv
from pyvcad_rendering import Render_Image

from fenicsx_solver import create_validated_mesh, solve_mixed_elasticity
from materials import (
    AGILUS30_DENSITY_G_CM3,
    AGILUS30_POISSONS_RATIO,
    AGILUS30_YOUNGS_MODULUS_MPA,
    VERO_DENSITY_G_CM3,
    VERO_POISSONS_RATIO,
    VERO_YOUNGS_MODULUS_MPA,
    illustrative_effective_properties,
)
from study_common import (
    allocate_monotonic_budget,
    compile_tet4_model,
    ensure_output_directory,
    lumped_point_volume_weights,
    matched_camera,
    normalize_with_bounds,
    preflight_coverage,
    render_settings,
    representative_box_samples,
    robust_bounds,
    volume_weighted_mean,
    write_json,
    write_result_bundle,
)


VERO_VOLUME_BUDGET = 0.35
ALLOCATION_SHARPNESS = 8.0
BUDGET_TOLERANCE = 1.0e-8

AGILUS_VISUAL_MATERIAL_ID = 10
VERO_VISUAL_MATERIAL_ID = 8

CANTILEVER_CENTER_MM = (15.0, 0.0, 0.0)
CANTILEVER_SIZE_MM = (30.0, 6.0, 6.0)
TRACTION_MPA = (0.0, 0.0, -5.0e-4)


def build_source_geometry():
    """Return the retained, centered OpenVCAD source cantilever."""
    return pv.RectPrism(
        pv.Vec3(*CANTILEVER_CENTER_MM),
        pv.Vec3(*CANTILEVER_SIZE_MM),
    )


def run_study(fast=False, render=True, output_name="study1_cantilever"):
    start_time = time.perf_counter()
    output_directory = ensure_output_directory(output_name)
    mesh_size = 3.0 if fast else 1.5
    clamp_distance = 1.5 * mesh_size
    render_quality = "low" if fast else "medium"
    render_width = 960 if fast else 1440
    render_height = 600 if fast else 900

    source_root = build_source_geometry()
    compiler, model, points, cells = compile_tet4_model(
        source_root,
        mesh_size,
        output_directory,
        "cantilever_source",
    )
    domain, ordering_metrics = create_validated_mesh(points, cells)

    cell_count = cells.shape[0]
    baseline_modulus = np.full(
        cell_count, AGILUS30_YOUNGS_MODULUS_MPA, dtype=np.float64
    )
    baseline_poissons_ratio = np.full(
        cell_count, AGILUS30_POISSONS_RATIO, dtype=np.float64
    )
    baseline = solve_mixed_elasticity(
        domain,
        points,
        baseline_modulus,
        baseline_poissons_ratio,
        TRACTION_MPA,
        solver_prefix="cantilever_baseline_",
    )

    projected_energy = baseline["projected_energy"]
    robust_minimum, robust_maximum = robust_bounds(projected_energy, 5.0, 95.0)
    normalized_signal = normalize_with_bounds(
        projected_energy, robust_minimum, robust_maximum
    )
    point_weights = lumped_point_volume_weights(points, cells)
    vero_fraction, allocation_offset, achieved_budget = allocate_monotonic_budget(
        normalized_signal,
        point_weights,
        VERO_VOLUME_BUDGET,
        ALLOCATION_SHARPNESS,
        BUDGET_TOLERANCE,
    )

    results = pv.UnstructuredFieldDataset.from_tetrahedra(points, cells)
    results.add_point_vector(
        "baseline_displacement",
        baseline["displacement"],
        units="mm",
        step_identifier="baseline",
        description="Taylor-Hood mixed-elasticity displacement",
    )
    results.add_point_scalar(
        "projected_strain_energy_density",
        projected_energy,
        units="mJ/mm^3",
        step_identifier="baseline",
        description="L2 projection of baseline strain-energy density to CG1 points",
    )
    results.add_point_scalar(
        "normalized_design_signal",
        normalized_signal,
        units="1",
        step_identifier="feedback",
        description="5th-to-95th percentile normalized and clamped energy signal",
    )
    results.add_point_scalar(
        "vero_fraction",
        vero_fraction,
        units="1",
        step_identifier="feedback",
        description="Bisection-budgeted monotonic Vero allocation",
    )

    sample_counts = (9, 4, 4) if fast else (21, 7, 7)
    representative_points = representative_box_samples(
        CANTILEVER_CENTER_MM, CANTILEVER_SIZE_MM, sample_counts
    )
    coverage = preflight_coverage(results, representative_points, clamp_distance)

    displacement_attribute = results.vec3_attribute(
        "baseline_displacement",
        outside="boundary_clamp",
        max_distance=clamp_distance,
    )
    energy_attribute = results.float_attribute(
        "projected_strain_energy_density",
        outside="boundary_clamp",
        max_distance=clamp_distance,
    )
    normalized_signal_attribute = results.float_attribute(
        "normalized_design_signal",
        outside="boundary_clamp",
        max_distance=clamp_distance,
    )
    vero_attribute = results.float_attribute(
        "vero_fraction",
        outside="boundary_clamp",
        max_distance=clamp_distance,
    )
    source_root.set_attribute(
        "baseline_displacement_magnitude", displacement_attribute.magnitude()
    )
    source_root.set_attribute("projected_strain_energy_density", energy_attribute)
    source_root.set_attribute("normalized_design_signal", normalized_signal_attribute)
    source_root.set_attribute("vero_fraction", vero_attribute)

    converter = pv.VolumeFractionsExpressionConverter(
        input_attributes=["vero_fraction"],
        materials=[AGILUS_VISUAL_MATERIAL_ID, VERO_VISUAL_MATERIAL_ID],
        expressions=["1.0 - vero_fraction", "vero_fraction"],
    )
    final_root = pv.AttributeModifier(converter, source_root)

    cell_vero_fraction = np.mean(vero_fraction[cells], axis=1)
    verification_modulus, verification_poissons_ratio = (
        illustrative_effective_properties(cell_vero_fraction)
    )
    verification = solve_mixed_elasticity(
        domain,
        points,
        verification_modulus,
        verification_poissons_ratio,
        TRACTION_MPA,
        solver_prefix="cantilever_verification_",
    )
    results.add_point_vector(
        "verification_displacement",
        verification["displacement"],
        units="mm",
        step_identifier="verification",
        description="Displacement after illustrative linear endpoint mixing",
    )

    xdmf_path, h5_path = write_result_bundle(
        output_directory,
        "cantilever_feedback_results",
        points,
        cells,
        {
            "baseline_displacement": (
                baseline["displacement"],
                "mm",
                "Baseline mixed displacement-pressure displacement",
            ),
            "projected_strain_energy_density": (
                projected_energy,
                "mJ/mm^3",
                "Continuous CG1 projection of strain-energy density",
            ),
            "normalized_design_signal": (
                normalized_signal,
                "1",
                "Robust bounded allocation control",
            ),
            "vero_fraction": (
                vero_fraction,
                "1",
                "Fixed-budget Vero volume fraction",
            ),
            "verification_displacement": (
                verification["displacement"],
                "mm",
                "Verification displacement using illustrative effective properties",
            ),
        },
        {
            "effective_youngs_modulus": (
                verification_modulus,
                "MPa",
                "Illustrative linear Agilus30/Vero mixture",
            ),
            "effective_poissons_ratio": (
                verification_poissons_ratio,
                "1",
                "Illustrative linear Agilus30/Vero mixture",
            ),
        },
    )

    render_paths = {}
    if render:
        camera = matched_camera(CANTILEVER_CENTER_MM, CANTILEVER_SIZE_MM)
        displacement_path = output_directory / "baseline_displacement.png"
        signal_path = output_directory / "projected_energy_signal.png"
        composition_path = output_directory / "final_composition.png"
        Render_Image(
            source_root,
            str(displacement_path),
            settings=render_settings(
                camera,
                "baseline_displacement_magnitude",
                render_quality,
                scalar_range=(0.0, baseline["metrics"]["maximum_displacement_mm"]),
            ),
            width=render_width,
            height=render_height,
        )
        Render_Image(
            source_root,
            str(signal_path),
            settings=render_settings(
                camera,
                "normalized_design_signal",
                render_quality,
                scalar_range=(0.0, 1.0),
                palette="turbo",
            ),
            width=render_width,
            height=render_height,
        )
        Render_Image(
            final_root,
            str(composition_path),
            settings=render_settings(
                camera,
                pv.DefaultAttributes.VOLUME_FRACTIONS,
                render_quality,
            ),
            width=render_width,
            height=render_height,
            materials=pv.default_materials,
        )
        render_paths = {
            "baseline_displacement": str(displacement_path),
            "projected_energy_signal": str(signal_path),
            "final_composition": str(composition_path),
        }

    metrics = {
        "study": "cantilever Agilus30/Vero feedback",
        "mode": "fast" if fast else "default",
        "mesh": {
            "target_cell_size_mm": mesh_size,
            "point_count": int(points.shape[0]),
            "cell_count": int(cells.shape[0]),
            "compiler_node_count": compiler.node_count(),
            "compiler_element_count": compiler.element_count(),
            "ordering_validation": ordering_metrics,
        },
        "material_endpoints": {
            "Agilus30": {
                "youngs_modulus_mpa": AGILUS30_YOUNGS_MODULUS_MPA,
                "poissons_ratio": AGILUS30_POISSONS_RATIO,
                "density_reference_g_cm3": AGILUS30_DENSITY_G_CM3,
            },
            "Vero": {
                "youngs_modulus_mpa": VERO_YOUNGS_MODULUS_MPA,
                "poissons_ratio": VERO_POISSONS_RATIO,
                "density_reference_g_cm3": VERO_DENSITY_G_CM3,
            },
        },
        "boundary_conditions": {
            "fixed": "all displacement components on x-min face",
            "traction_mpa": list(TRACTION_MPA),
            "loaded_region": "entire x-max face",
        },
        "baseline": baseline["metrics"],
        "projected_signal": {
            "raw_minimum": float(np.min(projected_energy)),
            "raw_maximum": float(np.max(projected_energy)),
            "robust_percentiles": [5.0, 95.0],
            "robust_minimum": robust_minimum,
            "robust_maximum": robust_maximum,
            "normalized_minimum": float(np.min(normalized_signal)),
            "normalized_maximum": float(np.max(normalized_signal)),
        },
        "coverage": coverage,
        "allocation": {
            "target_volume_weighted_vero_fraction": VERO_VOLUME_BUDGET,
            "achieved_volume_weighted_vero_fraction": achieved_budget,
            "independent_weighted_check": volume_weighted_mean(
                vero_fraction, point_weights
            ),
            "budget_absolute_error": abs(achieved_budget - VERO_VOLUME_BUDGET),
            "budget_tolerance": BUDGET_TOLERANCE,
            "sharpness": ALLOCATION_SHARPNESS,
            "bisection_offset": allocation_offset,
            "minimum_vero_fraction": float(np.min(vero_fraction)),
            "maximum_vero_fraction": float(np.max(vero_fraction)),
        },
        "effective_property_rule": {
            "kind": "linear endpoint mixture",
            "calibrated_polyjet_model": False,
            "minimum_cell_modulus_mpa": float(np.min(verification_modulus)),
            "maximum_cell_modulus_mpa": float(np.max(verification_modulus)),
            "minimum_cell_poissons_ratio": float(
                np.min(verification_poissons_ratio)
            ),
            "maximum_cell_poissons_ratio": float(
                np.max(verification_poissons_ratio)
            ),
        },
        "verification": verification["metrics"],
        "outputs": {
            "xdmf": str(xdmf_path),
            "hdf5": str(h5_path),
            "renders": render_paths,
        },
        "runtime_seconds": time.perf_counter() - start_time,
    }
    metrics_path = output_directory / "metrics.json"
    solver_log_path = output_directory / "solver.log"
    write_json(metrics_path, metrics)
    with open(solver_log_path, "w", encoding="utf-8") as stream:
        stream.write("Study 1 structural solves: exactly 2\n")
        stream.write("baseline={}\n".format(baseline["metrics"]))
        stream.write("verification={}\n".format(verification["metrics"]))
    metrics["outputs"]["metrics"] = str(metrics_path)
    metrics["outputs"]["solver_log"] = str(solver_log_path)
    return metrics
