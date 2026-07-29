"""
FEniCSx self-contained cantilever beam example
==============================================

This script builds a graded OpenVCAD beam, exports it to a script-local
FEniCSx XDMF/HDF5 bundle, reloads the exported mesh and cell fields, solves a
small-strain linear-elastic cantilever problem, and writes ParaView-ready
result files.

Install notes
-------------
- Create a DOLFINx environment from conda-forge:
  `conda create -n fenicsx -c conda-forge fenics-dolfinx mpi4py h5py numpy`
- Install the editable OpenVCAD packages into that same environment.
"""
import os

import h5py
import numpy as np
import pyvcad as pv
import pyvcad_compilers as pvc
import ufl
import xml.etree.ElementTree as ET
from mpi4py import MPI
from petsc4py import PETSc
from dolfinx import fem, mesh
from dolfinx.fem.petsc import LinearProblem
from dolfinx.io import XDMFFile

from lesson3_beam_definition import build_design

comm = MPI.COMM_WORLD
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")
xdmf_path = os.path.join(output_dir, "simulation_results.xdmf")
h5_path = os.path.join(output_dir, "simulation_results.h5")
face_tolerance = 0.05
traction_vector = np.array((0.0, 0.0, -5.0), dtype=PETSc.ScalarType)


def export_design():
    print("Exporting design for simulation from OpenVCAD...")
    os.makedirs(output_dir, exist_ok=True)
    root = build_design()

    direct_attributes = [
        pv.DefaultAttributes.MODULUS,
        pv.DefaultAttributes.POISSONS_RATIO,
    ]

    fenics_settings = pvc.SimulationCompilerSettings()
    fenics_settings.output_directory = output_dir
    fenics_settings.file_prefix = "simulation_results"
    fenics_settings.backend = pvc.SimulationBackend.FENICSX_XDMF
    fenics_settings.mesh_kind = pvc.SimulationMeshKind.TET
    fenics_settings.random_seed = 7
    fenics_settings.direct_attributes = direct_attributes

    tet_settings = pvc.SimulationTetFixedMeshSettings()
    tet_settings.facet_size = 0.75
    tet_settings.facet_distance = 0.75
    tet_settings.cell_size = 0.75
    fenics_settings.tet_fixed_settings = tet_settings

    compiler = pvc.SimulationCompiler(root, fenics_settings)
    compiler.compile()
    print("  -> Simulation files:", compiler.written_files())

def write_dataset(group, name, data):
    if name in group:
        del group[name]
    group.create_dataset(name, data=data)


def make_xdmf_attribute(name, center, attribute_type, dimensions, h5_dataset_path):
    attribute = ET.Element("Attribute", Name=name, AttributeType=attribute_type, Center=center)
    data_item = ET.SubElement(
        attribute,
        "DataItem",
        Format="HDF",
        DataType="Float",
        Precision="8",
        Dimensions=dimensions,
    )
    data_item.text = f"{os.path.basename(h5_path)}:{h5_dataset_path}"
    return attribute


def update_file_with_results(displacement_values, displacement_magnitude_values, von_mises_values):
    with h5py.File(h5_path, "a") as h5:
        node_group = h5.require_group("NodeData")
        cell_group = h5.require_group("CellData")
        write_dataset(node_group, "displacement", displacement_values)
        write_dataset(node_group, "displacement_magnitude", displacement_magnitude_values)
        write_dataset(cell_group, "von_mises", von_mises_values)

    tree = ET.parse(xdmf_path)
    root = tree.getroot()
    domain = root.find("Domain")
    export_grid = None
    for grid in domain.findall("Grid"):
        if grid.get("Name") == "OpenVCADMesh" and grid.get("GridType") == "Uniform":
            export_grid = grid
            break

    for attribute in list(export_grid.findall("Attribute")):
        if attribute.get("Name") in ("displacement", "displacement_magnitude", "von_mises"):
            export_grid.remove(attribute)

    export_grid.append(
        make_xdmf_attribute(
            "displacement",
            "Node",
            "Vector",
            f"{displacement_values.shape[0]} {displacement_values.shape[1]}",
            "/NodeData/displacement",
        )
    )
    export_grid.append(
        make_xdmf_attribute(
            "displacement_magnitude",
            "Node",
            "Scalar",
            f"{displacement_magnitude_values.shape[0]}",
            "/NodeData/displacement_magnitude",
        )
    )
    export_grid.append(
        make_xdmf_attribute(
            "von_mises",
            "Cell",
            "Scalar",
            f"{von_mises_values.shape[0]}",
            "/CellData/von_mises",
        )
    )

    ET.indent(tree, space="  ")
    tree.write(xdmf_path, encoding="utf-8", xml_declaration=True)

export_error = None
if comm.rank == 0:
    try:
        export_design()
    except Exception as exc:
        export_error = str(exc)

export_error = comm.bcast(export_error, root=0)
if export_error is not None:
    raise RuntimeError(f"OpenVCAD export failed on MPI rank 0: {export_error}")

with XDMFFile(comm, xdmf_path, "r") as xdmf:
    beam_mesh = xdmf.read_mesh(name="OpenVCADMesh")

cell_space = fem.functionspace(beam_mesh, ("DG", 0))
modulus = fem.Function(cell_space, name="modulus")
poissons_ratio = fem.Function(cell_space, name="poissons_ratio")

with h5py.File(h5_path, "r") as h5:
    modulus_data = np.asarray(h5["/CellData/modulus"])
    poissons_ratio_data = np.asarray(h5["/CellData/poissons_ratio"])

original_cell_index = np.asarray(beam_mesh.topology.original_cell_index, dtype=np.int64)

modulus.x.array[:] = modulus_data[original_cell_index]
poissons_ratio.x.array[:] = poissons_ratio_data[original_cell_index]

modulus.x.scatter_forward()
poissons_ratio.x.scatter_forward()

mu = modulus / (2.0 * (1.0 + poissons_ratio))
lmbda = modulus * poissons_ratio / ((1.0 + poissons_ratio) * (1.0 - 2.0 * poissons_ratio))


def epsilon(displacement):
    return ufl.sym(ufl.grad(displacement))


def sigma(displacement):
    return 2.0 * mu * epsilon(displacement) + lmbda * ufl.tr(epsilon(displacement)) * ufl.Identity(beam_mesh.geometry.dim)


displacement_space = fem.functionspace(beam_mesh, ("Lagrange", 1, (beam_mesh.geometry.dim,)))
u = ufl.TrialFunction(displacement_space)
v = ufl.TestFunction(displacement_space)

coords = beam_mesh.geometry.x
x_min = float(coords[:, 0].min())
x_max = float(coords[:, 0].max())
facet_dim = beam_mesh.topology.dim - 1

fixed_facets = mesh.locate_entities_boundary(
    beam_mesh,
    facet_dim,
    lambda x: x[0] < x_min + face_tolerance,
)
loaded_facets = mesh.locate_entities_boundary(
    beam_mesh,
    facet_dim,
    lambda x: x[0] > x_max - face_tolerance,
)

fixed_dofs = fem.locate_dofs_topological(displacement_space, facet_dim, fixed_facets)

zero_displacement = np.zeros(beam_mesh.geometry.dim, dtype=PETSc.ScalarType)
fixed_bc = fem.dirichletbc(zero_displacement, fixed_dofs, displacement_space)

loaded_facets = np.sort(loaded_facets.astype(np.int32))
load_tags = mesh.meshtags(
    beam_mesh,
    facet_dim,
    loaded_facets,
    np.full(loaded_facets.shape, 1, dtype=np.int32),
)
ds = ufl.Measure("ds", domain=beam_mesh, subdomain_data=load_tags)
traction = fem.Constant(beam_mesh, traction_vector)

a_form = ufl.inner(sigma(u), epsilon(v)) * ufl.dx
l_form = ufl.dot(traction, v) * ds(1)

problem = LinearProblem(
    a_form,
    l_form,
    petsc_options_prefix="beam_",
    bcs=[fixed_bc],
    petsc_options={
        "ksp_type": "preonly",
        "pc_type": "lu",
    },
)

print("Solving the linear system...")
displacement = problem.solve()
displacement.name = "displacement"
displacement.x.scatter_forward()

von_mises = fem.Function(cell_space, name="von_mises")
deviatoric_stress = sigma(displacement) - (ufl.tr(sigma(displacement)) / 3.0) * ufl.Identity(beam_mesh.geometry.dim)
von_mises_expr = fem.Expression(
    ufl.sqrt(1.5 * ufl.inner(deviatoric_stress, deviatoric_stress)),
    cell_space.element.interpolation_points,
)
von_mises.interpolate(von_mises_expr)
von_mises.x.scatter_forward()

displacement_values = displacement.x.array.reshape(-1, beam_mesh.geometry.dim)

local_geometry_points = beam_mesh.geometry.index_map().size_local
local_point_ids = np.asarray(beam_mesh.geometry.input_global_indices[:local_geometry_points], dtype=np.int64)
local_coordinates = coords[:local_geometry_points].copy()
local_displacement = displacement_values[:local_geometry_points].copy()

local_cell_count = beam_mesh.topology.index_map(beam_mesh.topology.dim).size_local
local_cell_ids = np.asarray(original_cell_index[:local_cell_count], dtype=np.int64)
local_von_mises = von_mises.x.array[:local_cell_count].copy()

point_id_chunks = comm.gather(local_point_ids, root=0)
coordinate_chunks = comm.gather(local_coordinates, root=0)
displacement_chunks = comm.gather(local_displacement, root=0)
cell_id_chunks = comm.gather(local_cell_ids, root=0)
von_mises_chunks = comm.gather(local_von_mises, root=0)

if comm.rank == 0:
    with h5py.File(h5_path, "r") as h5:
        point_count = h5["/Mesh/Geometry"].shape[0]
        cell_count = h5["/Mesh/Topology"].shape[0]

    global_coordinates = np.zeros((point_count, beam_mesh.geometry.dim), dtype=np.float64)
    global_displacement = np.zeros((point_count, beam_mesh.geometry.dim), dtype=np.float64)
    global_von_mises = np.zeros(cell_count, dtype=np.float64)
    active_node_mask = np.zeros(point_count, dtype=bool)

    for point_ids, point_coordinates, point_values in zip(point_id_chunks, coordinate_chunks, displacement_chunks):
        global_coordinates[point_ids] = point_coordinates
        global_displacement[point_ids] = point_values
        active_node_mask[point_ids] = True

    for cell_ids, cell_values in zip(cell_id_chunks, von_mises_chunks):
        global_von_mises[cell_ids] = cell_values

    global_displacement_magnitude = np.sqrt(np.sum(global_displacement * global_displacement, axis=1))

    update_file_with_results(global_displacement, global_displacement_magnitude, global_von_mises)

    x_coords = global_coordinates[active_node_mask, 0]
    active_displacement_magnitude = global_displacement_magnitude[active_node_mask]
    bin_edges = np.linspace(float(x_coords.min()), float(x_coords.max()), 6)

    print("Mean displacement magnitude by x-bin:")
    for index in range(5):
        lower = bin_edges[index]
        upper = bin_edges[index + 1]
        if index == 4:
            mask = (x_coords >= lower) & (x_coords <= upper)
            interval = "]"
        else:
            mask = (x_coords >= lower) & (x_coords < upper)
            interval = ")"

        mean_magnitude = float(np.mean(active_displacement_magnitude[mask]))
        print(f"  x in [{lower:6.2f}, {upper:6.2f}{interval}: mean |u| = {mean_magnitude:.6e}")

comm.barrier()

print("Simulation complete!")
print(f"  -> Results written to: {xdmf_path} and {h5_path}")
