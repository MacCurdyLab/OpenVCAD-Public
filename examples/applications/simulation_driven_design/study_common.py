"""Shared OpenVCAD-side helpers for the two FEniCSx feedback studies."""

import json
import math
import os
from pathlib import Path
import xml.etree.ElementTree as ET

import h5py
import numpy as np
import pyvcad as pv
import pyvcad_compilers as pvc


STUDY_DIRECTORY = Path(__file__).resolve().parent
REPOSITORY_ROOT = STUDY_DIRECTORY.parents[2]
OUTPUT_ROOT = REPOSITORY_ROOT / ".tmp" / "simulation_driven_design"


def ensure_output_directory(study_name):
    output_directory = OUTPUT_ROOT / study_name
    output_directory.mkdir(parents=True, exist_ok=True)
    return output_directory


def write_json(path, values):
    def convert(value):
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()
        raise TypeError("Unsupported JSON value: {}".format(type(value).__name__))

    with open(path, "w", encoding="utf-8") as stream:
        json.dump(values, stream, indent=2, sort_keys=True, default=convert)
        stream.write("\n")


def simulation_model_arrays(model):
    if model.cell_type != pvc.SimulationCellType.TET4:
        raise RuntimeError("The feedback studies require a TET4 SimulationModel")
    points = np.asarray(
        [[point.x, point.y, point.z] for point in model.nodes],
        dtype=np.float64,
    )
    cells = np.asarray(model.connectivity, dtype=np.int64).reshape((-1, 4))
    if cells.size == 0 or points.size == 0:
        raise RuntimeError("SimulationCompiler produced an empty TET4 model")
    return points, cells


def compile_tet4_model(root, mesh_size, output_directory, file_prefix):
    settings = pvc.SimulationCompilerSettings()
    settings.output_directory = str(output_directory)
    settings.file_prefix = file_prefix
    settings.backend = pvc.SimulationBackend.GENERIC
    settings.mesh_kind = pvc.SimulationMeshKind.TET
    settings.random_seed = 7

    tet_settings = pvc.SimulationTetFixedMeshSettings()
    tet_settings.facet_angle = 25.0
    tet_settings.facet_size = float(mesh_size)
    tet_settings.facet_distance = 0.25 * float(mesh_size)
    tet_settings.cell_radius_edge_ratio = 3
    tet_settings.cell_size = float(mesh_size)
    settings.tet_fixed_settings = tet_settings

    compiler = pvc.SimulationCompiler(root, settings)
    compiler.compile()
    model = compiler.model()
    points, cells = simulation_model_arrays(model)
    return compiler, model, points, cells


def tetrahedron_volumes(points, cells):
    coordinates = points[cells]
    matrices = np.stack(
        (
            coordinates[:, 1] - coordinates[:, 0],
            coordinates[:, 2] - coordinates[:, 0],
            coordinates[:, 3] - coordinates[:, 0],
        ),
        axis=2,
    )
    return np.abs(np.linalg.det(matrices)) / 6.0


def lumped_point_volume_weights(points, cells):
    volumes = tetrahedron_volumes(points, cells)
    weights = np.zeros(points.shape[0], dtype=np.float64)
    np.add.at(weights, cells.reshape(-1), np.repeat(volumes / 4.0, 4))
    if not np.all(np.isfinite(weights)) or float(np.sum(weights)) <= 0.0:
        raise RuntimeError("Invalid lumped TET4 point-volume weights")
    return weights


def volume_weighted_mean(values, weights):
    return float(np.dot(values, weights) / np.sum(weights))


def robust_bounds(values, lower_percentile=5.0, upper_percentile=95.0):
    values = np.asarray(values, dtype=np.float64)
    lower = float(np.percentile(values, lower_percentile))
    upper = float(np.percentile(values, upper_percentile))
    if not math.isfinite(lower) or not math.isfinite(upper):
        raise RuntimeError("Projected signal contains non-finite values")
    if upper <= lower:
        lower = float(np.min(values))
        upper = float(np.max(values))
    if upper <= lower:
        upper = lower + max(abs(lower), 1.0) * 1.0e-12
    return lower, upper


def normalize_with_bounds(values, lower, upper):
    return np.clip((np.asarray(values) - lower) / (upper - lower), 0.0, 1.0)


def allocate_monotonic_budget(signal, weights, target, sharpness, tolerance):
    signal = np.asarray(signal, dtype=np.float64)

    def fraction_for_offset(offset):
        argument = np.clip(sharpness * (signal - offset), -60.0, 60.0)
        return 1.0 / (1.0 + np.exp(-argument))

    lower = -8.0
    upper = 9.0
    for _ in range(160):
        midpoint = 0.5 * (lower + upper)
        fractions = fraction_for_offset(midpoint)
        achieved = volume_weighted_mean(fractions, weights)
        if abs(achieved - target) <= tolerance:
            break
        if achieved > target:
            lower = midpoint
        else:
            upper = midpoint
    fractions = np.clip(fraction_for_offset(midpoint), 0.0, 1.0)
    achieved = volume_weighted_mean(fractions, weights)
    if abs(achieved - target) > tolerance:
        raise RuntimeError(
            "Vero allocation budget error {:.3e} exceeds tolerance {:.3e}".format(
                abs(achieved - target), tolerance
            )
        )
    return fractions, midpoint, achieved


def representative_box_samples(center, size, counts):
    center = np.asarray(center, dtype=np.float64)
    size = np.asarray(size, dtype=np.float64)
    minimum = center - 0.5 * size
    maximum = center + 0.5 * size
    axes = [
        np.linspace(minimum[axis], maximum[axis], int(counts[axis]))
        for axis in range(3)
    ]
    grid = np.meshgrid(*axes, indexing="ij")
    return np.column_stack([component.reshape(-1) for component in grid])


def coverage_dictionary(report):
    return {
        "total_queries": report.total_queries,
        "inside_count": report.inside_count,
        "tolerance_adjusted_count": report.tolerance_adjusted_count,
        "boundary_clamped_count": report.boundary_clamped_count,
        "outside_count": report.outside_count,
        "maximum_clamp_distance": report.maximum_clamp_distance,
        "representative_failures": [
            {
                "position": [
                    failure.position.x,
                    failure.position.y,
                    failure.position.z,
                ],
                "boundary_distance": (
                    failure.boundary_distance
                    if math.isfinite(failure.boundary_distance)
                    else None
                ),
            }
            for failure in report.representative_failures
        ],
    }


def preflight_coverage(dataset, positions, clamp_distance):
    raw = dataset.coverage(positions, outside="error")
    clamped = dataset.coverage(
        positions,
        outside="boundary_clamp",
        max_distance=float(clamp_distance),
    )
    if clamped.outside_count != 0:
        raise RuntimeError(
            "Bounded field coverage left {} representative source samples outside".format(
                clamped.outside_count
            )
        )
    return {
        "raw": coverage_dictionary(raw),
        "bounded_clamp": coverage_dictionary(clamped),
        "clamp_band_mm": float(clamp_distance),
    }


def xdmf_data_item(parent, h5_name, dataset_path, dimensions, data_type, precision):
    item = ET.SubElement(
        parent,
        "DataItem",
        Format="HDF",
        DataType=data_type,
        Precision=str(precision),
        Dimensions=dimensions,
    )
    item.text = "{}:{}".format(h5_name, dataset_path)


def write_result_bundle(output_directory, prefix, points, cells, point_fields, cell_fields):
    h5_path = output_directory / (prefix + ".h5")
    xdmf_path = output_directory / (prefix + ".xdmf")

    with h5py.File(h5_path, "w") as h5_file:
        h5_file.create_dataset("/Mesh/Geometry", data=np.asarray(points, dtype=np.float64))
        h5_file.create_dataset("/Mesh/Topology", data=np.asarray(cells, dtype=np.int64))
        for name, field in point_fields.items():
            h5_file.create_dataset("/NodeData/" + name, data=np.asarray(field[0]))
        for name, field in cell_fields.items():
            h5_file.create_dataset("/CellData/" + name, data=np.asarray(field[0]))

    xdmf = ET.Element("Xdmf", Version="3.0")
    domain = ET.SubElement(xdmf, "Domain")
    grid = ET.SubElement(domain, "Grid", Name="OpenVCADFeedbackMesh", GridType="Uniform")
    topology = ET.SubElement(
        grid,
        "Topology",
        TopologyType="Tetrahedron",
        NumberOfElements=str(cells.shape[0]),
        NodesPerElement="4",
    )
    xdmf_data_item(
        topology,
        h5_path.name,
        "/Mesh/Topology",
        "{} 4".format(cells.shape[0]),
        "Int",
        8,
    )
    geometry = ET.SubElement(grid, "Geometry", GeometryType="XYZ")
    xdmf_data_item(
        geometry,
        h5_path.name,
        "/Mesh/Geometry",
        "{} 3".format(points.shape[0]),
        "Float",
        8,
    )

    def append_fields(fields, center, group):
        for name, field in fields.items():
            values, units, description = field
            values = np.asarray(values)
            component_count = 1 if values.ndim == 1 else values.shape[1]
            attribute_type = "Scalar" if component_count == 1 else "Vector"
            dimensions = str(values.shape[0])
            if component_count != 1:
                dimensions += " " + str(component_count)
            attribute = ET.SubElement(
                grid,
                "Attribute",
                Name=name,
                Center=center,
                AttributeType=attribute_type,
            )
            if units:
                attribute.set("Units", units)
            if description:
                attribute.set("Description", description)
            xdmf_data_item(
                attribute,
                h5_path.name,
                "/{}/{}".format(group, name),
                dimensions,
                "Float",
                8,
            )

    append_fields(point_fields, "Node", "NodeData")
    append_fields(cell_fields, "Cell", "CellData")
    tree = ET.ElementTree(xdmf)
    ET.indent(tree, space="  ")
    tree.write(xdmf_path, encoding="utf-8", xml_declaration=True)
    return xdmf_path, h5_path


def matched_camera(center, size):
    center = np.asarray(center, dtype=np.float64)
    size = np.asarray(size, dtype=np.float64)
    return {
        "position": [
            float(center[0] + 0.78 * size[0]),
            float(center[1] - 1.8 * max(size[1], 1.0)),
            float(center[2] + 1.35 * max(size[2], 1.0)),
        ],
        "focal_point": center.tolist(),
        "view_up": [0.0, 0.0, 1.0],
        "parallel_projection": True,
        "parallel_scale": float(0.75 * max(size[1], size[2], 0.65 * size[0])),
        "view_angle": 30.0,
    }


def render_settings(
    camera_state,
    attribute,
    quality,
    scalar_range=None,
    clipping=None,
    palette="viridis",
):
    settings = {
        "quality": quality,
        "render_mode": "iso_surface",
        "visualized_attribute": attribute,
        "scale_bar_palette": palette,
        "use_blending": True,
        "use_vol_shading": False,
        "show_bbox": False,
        "show_origin": False,
        "background_color": (0.96, 0.97, 0.98),
        "transparent_background": False,
        "scale_bar_visible": attribute not in ("none", pv.DefaultAttributes.VOLUME_FRACTIONS),
        "scale_bar_show_annotations": True,
        "camera_state": camera_state,
        "show_undefined_attribute_pattern": True,
    }
    if scalar_range is not None:
        settings.update(
            {
                "scalar_range_mode": "fixed",
                "scalar_range_min": float(scalar_range[0]),
                "scalar_range_max": float(scalar_range[1]),
            }
        )
    if clipping is not None:
        settings.update(
            {
                "clipping_plane": True,
                "clipping_plane_origin": clipping[0],
                "clipping_plane_normal": clipping[1],
            }
        )
    return settings


def env_flag(name):
    value = os.environ.get(name, "").strip().lower()
    return value in ("1", "true", "yes", "on")
