"""Generate, augment, and load a supported XDMF/HDF5 result bundle."""

from pathlib import Path
import xml.etree.ElementTree as ET

import h5py
import numpy as np
import pyvcad as pv
import pyvcad_compilers as pvc


repository_root = Path(__file__).resolve().parents[3]
output_directory = (
    repository_root
    / ".tmp"
    / "simulation_driven_design"
    / "public_xdmf_loader"
)
output_directory.mkdir(parents=True, exist_ok=True)
file_prefix = "public_result_bundle"

source_geometry = pv.RectPrism(pv.Vec3(5.0, 0.0, 0.0), pv.Vec3(10.0, 4.0, 4.0))
source_geometry.set_attribute("density", pv.FloatAttribute(1.18))

settings = pvc.SimulationCompilerSettings()
settings.backend = pvc.SimulationBackend.FENICSX_XDMF
settings.mesh_kind = pvc.SimulationMeshKind.TET
settings.output_directory = str(output_directory)
settings.file_prefix = file_prefix
settings.direct_attributes = ["density"]
settings.random_seed = 19

tet_settings = pvc.SimulationTetFixedMeshSettings()
tet_settings.facet_angle = 25.0
tet_settings.facet_size = 1.5
tet_settings.facet_distance = 0.4
tet_settings.cell_radius_edge_ratio = 3
tet_settings.cell_size = 1.5
settings.tet_fixed_settings = tet_settings

compiler = pvc.SimulationCompiler(source_geometry, settings)
compiler.compile()

xdmf_path = output_directory / (file_prefix + ".xdmf")
h5_path = output_directory / (file_prefix + ".h5")

with h5py.File(h5_path, "r+") as h5_file:
    points = np.asarray(h5_file["/Mesh/Geometry"], dtype=np.float64)
    cells = np.asarray(h5_file["/Mesh/Topology"], dtype=np.int64)
    point_group = h5_file.require_group("/NodeData")
    point_group.create_dataset(
        "temperature",
        data=22.0 + 0.4 * points[:, 0] + 0.2 * points[:, 2],
    )
    point_group.create_dataset(
        "displacement",
        data=np.column_stack(
            (0.01 * points[:, 0], np.zeros(points.shape[0]), -0.02 * points[:, 2])
        ),
    )

tree = ET.parse(xdmf_path)
grid = tree.getroot().find("./Domain/Grid")
if grid is None:
    raise RuntimeError("SimulationCompiler bundle did not contain one Uniform grid")


def add_result_attribute(name, attribute_type, dimensions, hdf_path, units):
    attribute = ET.SubElement(
        grid,
        "Attribute",
        Name=name,
        AttributeType=attribute_type,
        Center="Node",
        Units=units,
    )
    item = ET.SubElement(
        attribute,
        "DataItem",
        Format="HDF",
        DataType="Float",
        Precision="8",
        Dimensions=dimensions,
    )
    item.text = "{}:{}".format(h5_path.name, hdf_path)


add_result_attribute(
    "temperature",
    "Scalar",
    str(points.shape[0]),
    "/NodeData/temperature",
    "degC",
)
add_result_attribute(
    "displacement",
    "Vector",
    "{} 3".format(points.shape[0]),
    "/NodeData/displacement",
    "mm",
)
ET.indent(tree, space="  ")
tree.write(xdmf_path, encoding="utf-8", xml_declaration=True)

results = pv.XDMFFieldLoader.load(str(xdmf_path), grid_name="OpenVCADMesh")
print("Loaded:", xdmf_path)
print("Fields:")
for field_name in results.field_names:
    metadata = results.field_metadata(field_name)
    association = (
        "point" if metadata.association == pv.FieldAssociation.POINT else "cell"
    )
    print(
        "  {}: association={}, components={}, values={}, units={!r}".format(
            field_name,
            association,
            metadata.component_count,
            metadata.value_count,
            metadata.units,
        )
    )

temperature_attribute = results.float_attribute("temperature")
displacement_attribute = results.vec3_attribute("displacement")
density_attribute = results.float_attribute("density")

known_points = np.vstack(
    (
        points[cells[0]].mean(axis=0),
        points[cells[len(cells) // 2]].mean(axis=0),
        points[cells[-1]].mean(axis=0),
    )
)
print("Known interior samples:")
for point in known_points:
    displacement_value = displacement_attribute.sample(*point, 0.0)
    print(
        "  p={} temperature={:.6f} displacement=({:.6f}, {:.6f}, {:.6f}) "
        "density={:.3f}".format(
            point.tolist(),
            temperature_attribute.sample(*point, 0.0),
            displacement_value.x,
            displacement_value.y,
            displacement_value.z,
            density_attribute.sample(*point, 0.0),
        )
    )

coverage = results.coverage(known_points, outside="error")
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
    raise RuntimeError("Known public-loader sample points were not covered")
