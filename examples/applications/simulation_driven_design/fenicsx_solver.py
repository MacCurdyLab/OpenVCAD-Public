"""DOLFINx mesh validation, mixed elasticity, and point-field projection."""

import math

import basix.ufl
from dolfinx import fem, mesh
from dolfinx.fem.petsc import LinearProblem
from mpi4py import MPI
import numpy as np
from petsc4py import PETSc
import ufl


def create_validated_mesh(points, cells):
    """Create a serial DOLFINx TET4 mesh and verify input/global ordering."""
    comm = MPI.COMM_WORLD
    if comm.size != 1:
        raise RuntimeError(
            "These study entry points are validated for serial execution only; "
            "MPI gathering is intentionally not claimed."
        )

    coordinate_element = basix.ufl.element(
        "Lagrange", "tetrahedron", 1, shape=(points.shape[1],)
    )
    domain = mesh.create_mesh(
        comm,
        np.asarray(cells, dtype=np.int64),
        coordinate_element,
        np.asarray(points, dtype=np.float64),
    )

    geometry_map = domain.geometry.index_map()
    owned_points = geometry_map.size_local
    input_point_ids = np.asarray(
        domain.geometry.input_global_indices[:owned_points], dtype=np.int64
    )
    local_coordinates = np.asarray(domain.geometry.x[:owned_points, :3])
    coordinate_error = float(
        np.max(np.linalg.norm(local_coordinates - points[input_point_ids], axis=1))
    )

    cell_map = domain.topology.index_map(domain.topology.dim)
    owned_cells = cell_map.size_local
    original_cell_ids = np.asarray(
        domain.topology.original_cell_index[:owned_cells], dtype=np.int64
    )
    geometry_dofmap = np.asarray(domain.geometry.dofmap[:owned_cells, :4])
    local_cell_point_ids = input_point_ids[geometry_dofmap]
    expected_cell_point_ids = cells[original_cell_ids]
    cell_order_matches = np.all(
        np.sort(local_cell_point_ids, axis=1)
        == np.sort(expected_cell_point_ids, axis=1)
    )
    point_ids_complete = np.array_equal(
        np.sort(input_point_ids), np.arange(points.shape[0], dtype=np.int64)
    )
    cell_ids_complete = np.array_equal(
        np.sort(original_cell_ids), np.arange(cells.shape[0], dtype=np.int64)
    )

    validation_tolerance = 1.0e-11 * max(
        1.0, float(np.max(np.abs(points)))
    )
    if coordinate_error > validation_tolerance:
        raise RuntimeError(
            "DOLFINx geometry/input point mapping error {:.3e} exceeds {:.3e}".format(
                coordinate_error, validation_tolerance
            )
        )
    if not point_ids_complete or not cell_ids_complete or not cell_order_matches:
        raise RuntimeError("DOLFINx serial/global point or cell index validation failed")

    analytic_scalar = points[:, 0] + 2.0 * points[:, 1] - 0.5 * points[:, 2]
    analytic_vector = np.column_stack(
        (points[:, 0], points[:, 1] - points[:, 2], 2.0 * points[:, 2])
    )
    scalar_space = fem.functionspace(domain, ("Lagrange", 1))
    vector_space = fem.functionspace(domain, ("Lagrange", 1, (3,)))
    scalar_function = fem.Function(scalar_space)
    vector_function = fem.Function(vector_space)
    scalar_function.interpolate(lambda x: x[0] + 2.0 * x[1] - 0.5 * x[2])
    vector_function.interpolate(
        lambda x: np.vstack((x[0], x[1] - x[2], 2.0 * x[2]))
    )
    recovered_scalar, scalar_coordinate_error = point_values_in_input_order(
        scalar_function, points, component_count=1
    )
    recovered_vector, vector_coordinate_error = point_values_in_input_order(
        vector_function, points, component_count=3
    )
    analytic_scalar_error = float(np.max(np.abs(recovered_scalar - analytic_scalar)))
    analytic_vector_error = float(np.max(np.abs(recovered_vector - analytic_vector)))
    if analytic_scalar_error > validation_tolerance:
        raise RuntimeError("Analytic scalar point-ordering validation failed")
    if analytic_vector_error > validation_tolerance:
        raise RuntimeError("Analytic vector point-ordering validation failed")

    return domain, {
        "mpi_size": comm.size,
        "point_ids_complete": bool(point_ids_complete),
        "cell_ids_complete": bool(cell_ids_complete),
        "cell_connectivity_matches_input": bool(cell_order_matches),
        "maximum_geometry_coordinate_error": coordinate_error,
        "analytic_scalar_error": analytic_scalar_error,
        "analytic_vector_error": analytic_vector_error,
        "scalar_dof_coordinate_error": scalar_coordinate_error,
        "vector_dof_coordinate_error": vector_coordinate_error,
        "input_point_count": int(points.shape[0]),
        "input_cell_count": int(cells.shape[0]),
    }


def point_values_in_input_order(function, input_points, component_count):
    """Map owned P1 DOF values to the original SimulationModel point order."""
    function.x.scatter_forward()
    space = function.function_space
    index_map = space.dofmap.index_map
    block_size = space.dofmap.index_map_bs
    if block_size != component_count:
        raise RuntimeError(
            "Expected P1 block size {}, found {}".format(component_count, block_size)
        )
    owned_blocks = index_map.size_local
    coordinates = np.asarray(space.tabulate_dof_coordinates()[:owned_blocks, :3])
    values = np.asarray(function.x.array[: owned_blocks * block_size])
    if component_count == 1:
        values = values.reshape((-1,))
        result = np.full(input_points.shape[0], np.nan, dtype=np.float64)
    else:
        values = values.reshape((-1, component_count))
        result = np.full(
            (input_points.shape[0], component_count), np.nan, dtype=np.float64
        )

    coordinate_lookup = {}
    for point_index, point in enumerate(input_points):
        coordinate_lookup[tuple(np.round(point, decimals=11))] = point_index

    maximum_coordinate_error = 0.0
    for dof_index, coordinate in enumerate(coordinates):
        key = tuple(np.round(coordinate, decimals=11))
        point_index = coordinate_lookup.get(key)
        if point_index is None:
            distances = np.linalg.norm(input_points - coordinate, axis=1)
            point_index = int(np.argmin(distances))
            maximum_coordinate_error = max(
                maximum_coordinate_error, float(distances[point_index])
            )
        else:
            maximum_coordinate_error = max(
                maximum_coordinate_error,
                float(np.linalg.norm(input_points[point_index] - coordinate)),
            )
        result[point_index] = values[dof_index]

    if np.any(~np.isfinite(result)):
        raise RuntimeError("P1 output gathering did not populate every input mesh point")
    tolerance = 1.0e-10 * max(1.0, float(np.max(np.abs(input_points))))
    if maximum_coordinate_error > tolerance:
        raise RuntimeError("P1 DOF coordinates do not match SimulationModel points")
    return result, maximum_coordinate_error


def assign_cell_field(function, values, domain):
    cell_count = domain.topology.index_map(domain.topology.dim).size_local
    original_ids = np.asarray(
        domain.topology.original_cell_index[:cell_count], dtype=np.int64
    )
    function.x.array[:cell_count] = np.asarray(values)[original_ids]
    function.x.scatter_forward()


def project_scalar_to_p1(domain, expression, prefix):
    scalar_space = fem.functionspace(domain, ("Lagrange", 1))
    trial = ufl.TrialFunction(scalar_space)
    test = ufl.TestFunction(scalar_space)
    problem = LinearProblem(
        ufl.inner(trial, test) * ufl.dx,
        ufl.inner(expression, test) * ufl.dx,
        petsc_options_prefix=prefix,
        petsc_options={"ksp_type": "preonly", "pc_type": "lu"},
    )
    projected = problem.solve()
    projected.x.scatter_forward()
    return projected, {
        "converged_reason": int(problem.solver.getConvergedReason()),
        "iterations": int(problem.solver.getIterationNumber()),
    }


def solve_mixed_elasticity(
    domain,
    input_points,
    modulus_by_cell,
    poissons_ratio_by_cell,
    traction_vector,
    load_region="full_end",
    solver_prefix="feedback_",
):
    """Solve locking-resistant Taylor-Hood displacement-pressure elasticity."""
    geometric_dimension = domain.geometry.dim
    cell_name = domain.basix_cell()
    displacement_element = basix.ufl.element(
        "Lagrange", cell_name, 2, shape=(geometric_dimension,)
    )
    pressure_element = basix.ufl.element("Lagrange", cell_name, 1)
    mixed_element = basix.ufl.mixed_element(
        [displacement_element, pressure_element]
    )
    mixed_space = fem.functionspace(domain, mixed_element)

    cell_space = fem.functionspace(domain, ("DG", 0))
    modulus = fem.Function(cell_space, name="youngs_modulus_mpa")
    poissons_ratio = fem.Function(cell_space, name="poissons_ratio")
    assign_cell_field(modulus, modulus_by_cell, domain)
    assign_cell_field(poissons_ratio, poissons_ratio_by_cell, domain)

    shear_modulus = modulus / (2.0 * (1.0 + poissons_ratio))
    bulk_modulus = modulus / (3.0 * (1.0 - 2.0 * poissons_ratio))

    displacement, pressure = ufl.TrialFunctions(mixed_space)
    displacement_test, pressure_test = ufl.TestFunctions(mixed_space)
    strain = ufl.sym(ufl.grad(displacement))
    test_strain = ufl.sym(ufl.grad(displacement_test))
    deviatoric_strain = ufl.dev(strain)
    deviatoric_test_strain = ufl.dev(test_strain)

    coordinates = domain.geometry.x
    x_min = float(np.min(coordinates[:, 0]))
    x_max = float(np.max(coordinates[:, 0]))
    y_mid = 0.5 * (
        float(np.min(coordinates[:, 1])) + float(np.max(coordinates[:, 1]))
    )
    # CGAL's implicit-domain TET mesher approximates even planar source faces,
    # so select the end caps with a narrow geometric band rather than assuming
    # vertices lie at one bit-identical x coordinate.
    face_tolerance = 0.02 * max(1.0, x_max - x_min)
    facet_dimension = domain.topology.dim - 1
    fixed_facets = mesh.locate_entities_boundary(
        domain,
        facet_dimension,
        lambda x: x[0] <= x_min + face_tolerance,
    )
    if load_region == "upper_half_end":
        loaded_facets = mesh.locate_entities_boundary(
            domain,
            facet_dimension,
            lambda x: np.logical_and(
                x[0] >= x_max - face_tolerance,
                x[1] >= y_mid - face_tolerance,
            ),
        )
    else:
        loaded_facets = mesh.locate_entities_boundary(
            domain,
            facet_dimension,
            lambda x: x[0] >= x_max - face_tolerance,
        )
    if fixed_facets.size == 0 or loaded_facets.size == 0:
        raise RuntimeError("Failed to locate fixed or loaded exterior facets")

    collapsed_displacement_space, _ = mixed_space.sub(0).collapse()
    fixed_dofs = fem.locate_dofs_topological(
        (mixed_space.sub(0), collapsed_displacement_space),
        facet_dimension,
        fixed_facets,
    )
    zero_displacement = fem.Function(collapsed_displacement_space)
    zero_displacement.x.array[:] = 0.0
    fixed_boundary = fem.dirichletbc(
        zero_displacement, fixed_dofs, mixed_space.sub(0)
    )

    loaded_facets = np.sort(np.asarray(loaded_facets, dtype=np.int32))
    load_tags = mesh.meshtags(
        domain,
        facet_dimension,
        loaded_facets,
        np.ones(loaded_facets.shape, dtype=np.int32),
    )
    surface_measure = ufl.Measure("ds", domain=domain, subdomain_data=load_tags)
    traction = fem.Constant(
        domain, np.asarray(traction_vector, dtype=PETSc.ScalarType)
    )

    bilinear_form = (
        2.0
        * shear_modulus
        * ufl.inner(deviatoric_strain, deviatoric_test_strain)
        * ufl.dx
        - pressure * ufl.div(displacement_test) * ufl.dx
        - pressure_test * ufl.div(displacement) * ufl.dx
        - (pressure * pressure_test / bulk_modulus) * ufl.dx
    )
    linear_form = ufl.dot(traction, displacement_test) * surface_measure(1)

    problem = LinearProblem(
        bilinear_form,
        linear_form,
        petsc_options_prefix=solver_prefix,
        bcs=[fixed_boundary],
        petsc_options={"ksp_type": "preonly", "pc_type": "lu"},
    )
    solution = problem.solve()
    solution.x.scatter_forward()
    converged_reason = int(problem.solver.getConvergedReason())
    if converged_reason <= 0:
        raise RuntimeError(
            "Mixed elasticity solve did not converge; PETSc reason {}".format(
                converged_reason
            )
        )

    displacement_solution = solution.sub(0).collapse()
    point_displacement_space = fem.functionspace(
        domain, ("Lagrange", 1, (geometric_dimension,))
    )
    point_displacement = fem.Function(
        point_displacement_space, name="displacement"
    )
    point_displacement.interpolate(displacement_solution)
    point_displacement.x.scatter_forward()

    solved_displacement, solved_pressure = ufl.split(solution)
    solved_strain = ufl.sym(ufl.grad(solved_displacement))
    energy_density_expression = (
        shear_modulus * ufl.inner(ufl.dev(solved_strain), ufl.dev(solved_strain))
        + 0.5 * solved_pressure * solved_pressure / bulk_modulus
    )
    projected_energy, projection_metrics = project_scalar_to_p1(
        domain, energy_density_expression, solver_prefix + "energy_projection_"
    )

    displacement_values, displacement_coordinate_error = point_values_in_input_order(
        point_displacement, input_points, component_count=3
    )
    energy_values, energy_coordinate_error = point_values_in_input_order(
        projected_energy, input_points, component_count=1
    )
    # A continuous L2 projection can exhibit small negative nodal overshoots
    # even though the underlying quadrature-point energy is non-negative.
    # Enforce the physical lower bound before handing the control field back to
    # OpenVCAD and report the correction explicitly.
    projected_minimum_before_clamp = float(np.min(energy_values))
    projected_negative_count = int(np.count_nonzero(energy_values < 0.0))
    energy_values = np.maximum(energy_values, 0.0)

    local_compliance = fem.assemble_scalar(
        fem.form(
            ufl.dot(traction, solved_displacement) * surface_measure(1)
        )
    )
    compliance = domain.comm.allreduce(local_compliance, op=MPI.SUM)
    local_energy = fem.assemble_scalar(
        fem.form(energy_density_expression * ufl.dx)
    )
    strain_energy = domain.comm.allreduce(local_energy, op=MPI.SUM)
    maximum_displacement = float(
        np.max(np.linalg.norm(displacement_values, axis=1))
    )

    return {
        "displacement": displacement_values,
        "projected_energy": energy_values,
        "metrics": {
            "maximum_displacement_mm": maximum_displacement,
            "compliance_mj": float(compliance),
            "strain_energy_mj": float(strain_energy),
            "compliance_to_twice_energy_ratio": float(
                compliance / (2.0 * strain_energy)
            )
            if strain_energy != 0.0
            else math.nan,
            "solver_converged_reason": converged_reason,
            "solver_iterations": int(problem.solver.getIterationNumber()),
            "energy_projection": projection_metrics,
            "projected_minimum_before_nonnegative_clamp": projected_minimum_before_clamp,
            "projected_negative_node_count": projected_negative_count,
            "displacement_dof_coordinate_error": displacement_coordinate_error,
            "energy_dof_coordinate_error": energy_coordinate_error,
            "fixed_facet_count": int(fixed_facets.size),
            "loaded_facet_count": int(loaded_facets.size),
            "formulation": "Taylor-Hood P2 displacement / P1 pressure",
        },
    }
