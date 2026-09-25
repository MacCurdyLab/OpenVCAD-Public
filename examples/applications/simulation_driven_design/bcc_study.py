"""Study 2 implementation: result-driven BCC beam radius."""

import time

import numpy as np
import pyvcad as pv
import pyvcad_metamaterials as mm
from pyvcad_rendering import Render_Image

from fenicsx_solver import create_validated_mesh, solve_mixed_elasticity
from study_common import (
    compile_tet4_model,
    ensure_output_directory,
    matched_camera,
    normalize_with_bounds,
    preflight_coverage,
    render_settings,
    representative_box_samples,
    robust_bounds,
    write_json,
    write_result_bundle,
)


ENVELOPE_CENTER_MM = (18.0, 0.0, 0.0)
ENVELOPE_SIZE_MM = (36.0, 12.0, 12.0)
SOLID_YOUNGS_MODULUS_MPA = 1200.0
SOLID_POISSONS_RATIO = 0.35
TRACTION_MPA = (0.0, 0.0, -0.08)

MINIMUM_BEAM_RADIUS_MM = 0.55
MAXIMUM_BEAM_RADIUS_MM = 1.30
CONSTANT_BEAM_RADIUS_MM = 0.90
RAW_SIGNAL_ATTRIBUTE = "projected_strain_energy_density"
RADIUS_ATTRIBUTE = "beam_radius_control"


def build_source_envelope():
    return pv.RectPrism(
        pv.Vec3(*ENVELOPE_CENTER_MM),
        pv.Vec3(*ENVELOPE_SIZE_MM),
    )


def lattice_map(fast):
    half_size = 0.5 * np.asarray(ENVELOPE_SIZE_MM)
    center = np.asarray(ENVELOPE_CENTER_MM)
    minimum = center - half_size
    maximum = center + half_size
    cell_counts = (6, 2, 2) if fast else (9, 3, 3)
    return mm.rectangular_cell_map(
        (pv.Vec3(*minimum), pv.Vec3(*maximum)), cells=cell_counts
    ), cell_counts


def run_study(fast=False, render=True, output_name="study2_bcc"):
    start_time = time.perf_counter()
    output_directory = ensure_output_directory(output_name)
    mesh_size = 3.6 if fast else 1.8
    clamp_distance = 1.5 * mesh_size
    render_quality = "low" if fast else "medium"
    render_width = 960 if fast else 1440
    render_height = 600 if fast else 900

    source_envelope = build_source_envelope()
    compiler, model, points, cells = compile_tet4_model(
        source_envelope,
        mesh_size,
        output_directory,
        "bcc_source_envelope",
    )
    domain, ordering_metrics = create_validated_mesh(points, cells)
    cell_count = cells.shape[0]
    analysis = solve_mixed_elasticity(
        domain,
        points,
        np.full(cell_count, SOLID_YOUNGS_MODULUS_MPA, dtype=np.float64),
        np.full(cell_count, SOLID_POISSONS_RATIO, dtype=np.float64),
        TRACTION_MPA,
        load_region="upper_half_end",
        solver_prefix="bcc_envelope_",
    )

    projected_energy = analysis["projected_energy"]
    robust_minimum, robust_maximum = robust_bounds(projected_energy, 5.0, 95.0)
    normalized_signal = normalize_with_bounds(
        projected_energy, robust_minimum, robust_maximum
    )
    nodal_radius = (
        MINIMUM_BEAM_RADIUS_MM
        + (MAXIMUM_BEAM_RADIUS_MM - MINIMUM_BEAM_RADIUS_MM) * normalized_signal
    )

    results = pv.UnstructuredFieldDataset.from_tetrahedra(points, cells)
    results.add_point_scalar(
        RAW_SIGNAL_ATTRIBUTE,
        projected_energy,
        units="mJ/mm^3",
        step_identifier="solid_envelope",
        description="L2-projected solid-envelope strain-energy density",
    )
    results.add_point_scalar(
        "normalized_design_signal",
        normalized_signal,
        units="1",
        step_identifier="feedback",
        description="5th-to-95th percentile bounded energy control",
    )

    sample_counts = (9, 4, 4) if fast else (21, 7, 7)
    representative_points = representative_box_samples(
        ENVELOPE_CENTER_MM, ENVELOPE_SIZE_MM, sample_counts
    )
    coverage = preflight_coverage(results, representative_points, clamp_distance)

    raw_signal_attribute = results.float_attribute(
        RAW_SIGNAL_ATTRIBUTE,
        outside="boundary_clamp",
        max_distance=clamp_distance,
    )
    bounded_signal_attribute = raw_signal_attribute.normalize(
        robust_minimum, robust_maximum
    ).clamp(0.0, 1.0)
    radius_attribute = bounded_signal_attribute.map_range(
        0.0,
        1.0,
        MINIMUM_BEAM_RADIUS_MM,
        MAXIMUM_BEAM_RADIUS_MM,
    )
    source_envelope.set_attribute(RAW_SIGNAL_ATTRIBUTE, raw_signal_attribute)
    source_envelope.set_attribute("normalized_design_signal", bounded_signal_attribute)

    constant_map, cell_counts = lattice_map(fast)
    driven_map, _ = lattice_map(fast)
    constant_lattice = mm.bcc(
        constant_map,
        beam_radius=CONSTANT_BEAM_RADIUS_MM,
        node_radius=CONSTANT_BEAM_RADIUS_MM,
    )
    driven_lattice = mm.bcc(
        driven_map,
        beam_radius=radius_attribute,
        node_radius=radius_attribute,
    )
    constant_root = pv.Intersection(constant_lattice, build_source_envelope())
    driven_root = pv.Intersection(driven_lattice, build_source_envelope())
    constant_root.set_attribute(RAW_SIGNAL_ATTRIBUTE, raw_signal_attribute)
    constant_root.set_attribute(
        RADIUS_ATTRIBUTE, pv.FloatAttribute(CONSTANT_BEAM_RADIUS_MM)
    )
    driven_root.set_attribute(RAW_SIGNAL_ATTRIBUTE, raw_signal_attribute)
    driven_root.set_attribute(RADIUS_ATTRIBUTE, radius_attribute)

    volume_sample_size = 1.0 if fast else 0.6
    volume_voxel = pv.Vec3(
        volume_sample_size, volume_sample_size, volume_sample_size
    )
    constant_root.prepare(volume_voxel, 3.0 * volume_sample_size)
    driven_root.prepare(volume_voxel, 3.0 * volume_sample_size)
    constant_volume = float(constant_root.volume(volume_sample_size))
    driven_volume = float(driven_root.volume(volume_sample_size))
    relative_volume_difference = (
        (driven_volume - constant_volume) / constant_volume
        if constant_volume != 0.0
        else float("nan")
    )

    xdmf_path, h5_path = write_result_bundle(
        output_directory,
        "bcc_feedback_results",
        points,
        cells,
        {
            RAW_SIGNAL_ATTRIBUTE: (
                projected_energy,
                "mJ/mm^3",
                "Continuous solid-envelope strain-energy signal",
            ),
            "normalized_design_signal": (
                normalized_signal,
                "1",
                "Robust bounded geometry control",
            ),
            RADIUS_ATTRIBUTE: (
                nodal_radius,
                "mm",
                "Result-driven bounded BCC beam radius",
            ),
        },
        {},
    )

    render_paths = {}
    if render:
        camera = matched_camera(ENVELOPE_CENTER_MM, ENVELOPE_SIZE_MM)
        clipping = (
            [ENVELOPE_CENTER_MM[0], ENVELOPE_CENTER_MM[1], ENVELOPE_CENTER_MM[2]],
            [0.0, -1.0, 0.0],
        )
        constant_path = output_directory / "constant_radius_bcc.png"
        driven_path = output_directory / "result_driven_bcc.png"
        signal_path = output_directory / "solid_projected_energy.png"
        matched_radius_settings = render_settings(
            camera,
            RADIUS_ATTRIBUTE,
            render_quality,
            scalar_range=(MINIMUM_BEAM_RADIUS_MM, MAXIMUM_BEAM_RADIUS_MM),
            clipping=clipping,
        )
        Render_Image(
            constant_root,
            str(constant_path),
            settings=matched_radius_settings,
            width=render_width,
            height=render_height,
        )
        Render_Image(
            driven_root,
            str(driven_path),
            settings=matched_radius_settings,
            width=render_width,
            height=render_height,
        )
        Render_Image(
            source_envelope,
            str(signal_path),
            settings=render_settings(
                camera,
                "normalized_design_signal",
                render_quality,
                scalar_range=(0.0, 1.0),
                clipping=clipping,
                palette="turbo",
            ),
            width=render_width,
            height=render_height,
        )
        render_paths = {
            "constant_radius_bcc": str(constant_path),
            "result_driven_bcc": str(driven_path),
            "solid_projected_energy": str(signal_path),
        }

    metrics = {
        "study": "result-driven BCC beam radius",
        "mode": "fast" if fast else "default",
        "mesh": {
            "target_cell_size_mm": mesh_size,
            "point_count": int(points.shape[0]),
            "cell_count": int(cells.shape[0]),
            "compiler_node_count": compiler.node_count(),
            "compiler_element_count": compiler.element_count(),
            "ordering_validation": ordering_metrics,
        },
        "solid_analysis": analysis["metrics"],
        "boundary_conditions": {
            "fixed": "all displacement components on x-min face",
            "traction_mpa": list(TRACTION_MPA),
            "loaded_region": "upper half of x-max face",
        },
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
        "radius": {
            "minimum_bound_mm": MINIMUM_BEAM_RADIUS_MM,
            "maximum_bound_mm": MAXIMUM_BEAM_RADIUS_MM,
            "observed_minimum_mm": float(np.min(nodal_radius)),
            "observed_maximum_mm": float(np.max(nodal_radius)),
            "constant_comparison_mm": CONSTANT_BEAM_RADIUS_MM,
            "cell_counts": list(cell_counts),
        },
        "estimated_material_usage": {
            "sampling_resolution_mm": volume_sample_size,
            "constant_radius_volume_mm3": constant_volume,
            "result_driven_volume_mm3": driven_volume,
            "relative_difference": relative_volume_difference,
            "relative_difference_percent": 100.0 * relative_volume_difference,
        },
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
        stream.write("Study 2 structural solves: exactly 1\n")
        stream.write("solid_envelope={}\n".format(analysis["metrics"]))
        stream.write("No lattice verification solve is part of Task 2.\n")
    metrics["outputs"]["metrics"] = str(metrics_path)
    metrics["outputs"]["solver_log"] = str(solver_log_path)
    return metrics
