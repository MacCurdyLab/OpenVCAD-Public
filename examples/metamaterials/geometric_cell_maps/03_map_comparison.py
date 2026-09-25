"""Compare one BCC cell family in rectangular, cylindrical, and spherical maps."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


# Pipe comparison: both lattices are clipped by the same annular pipe envelope.
rectangular_pipe_center = pv.Vec3(-28.0, -32.0, 0.0)
cylindrical_pipe_center = pv.Vec3(28.0, -32.0, 0.0)
pipe_inner_radius = 12.0
pipe_outer_radius = 17.0
pipe_height = 30.0

rectangular_pipe_map = mm.rectangular_cell_map(
    (
        pv.Vec3(-45.0, -49.0, -15.0),
        pv.Vec3(-11.0, -15.0, 15.0),
    ),
    cells=(6, 6, 5),
)
rectangular_pipe_lattice = mm.bcc(rectangular_pipe_map, beam_radius=0.55)
rectangular_pipe_envelope = pv.Difference(
    pv.Cylinder(rectangular_pipe_center, pipe_outer_radius, pipe_height),
    pv.Cylinder(rectangular_pipe_center, pipe_inner_radius, pipe_height + 2.0),
)
rectangular_pipe = pv.Intersection(
    rectangular_pipe_lattice,
    rectangular_pipe_envelope,
)

cylindrical_pipe_map = mm.cylindrical_cell_map(
    center=cylindrical_pipe_center,
    inner_radius=pipe_inner_radius,
    outer_radius=pipe_outer_radius,
    height=pipe_height,
    cells=(16, 5, 2),
)
cylindrical_pipe_lattice = mm.bcc(cylindrical_pipe_map, beam_radius=0.55)
cylindrical_pipe_envelope = pv.Difference(
    pv.Cylinder(cylindrical_pipe_center, pipe_outer_radius, pipe_height),
    pv.Cylinder(cylindrical_pipe_center, pipe_inner_radius, pipe_height + 2.0),
)
cylindrical_pipe = pv.Intersection(
    cylindrical_pipe_lattice,
    cylindrical_pipe_envelope,
)
pipe_comparison = pv.Union(rectangular_pipe, cylindrical_pipe)


# Shell comparison: both lattices are clipped by the same shell and waist slab.
rectangular_shell_center = pv.Vec3(-28.0, 32.0, 0.0)
spherical_shell_center = pv.Vec3(28.0, 32.0, 0.0)
shell_inner_radius = 13.0
shell_outer_radius = 18.0
slab_half_height = 13.0

rectangular_shell_map = mm.rectangular_cell_map(
    (
        pv.Vec3(-46.0, 14.0, -18.0),
        pv.Vec3(-10.0, 50.0, 18.0),
    ),
    cells=(6, 6, 6),
)
rectangular_shell_lattice = mm.bcc(rectangular_shell_map, beam_radius=0.55)
rectangular_shell_envelope = pv.Intersection(
    pv.Difference(
        pv.Sphere(rectangular_shell_center, shell_outer_radius),
        pv.Sphere(rectangular_shell_center, shell_inner_radius),
    ),
    pv.RectPrism.FromMinAndMax(
        pv.Vec3(-47.0, 13.0, -slab_half_height),
        pv.Vec3(-9.0, 51.0, slab_half_height),
    ),
)
rectangular_shell = pv.Intersection(
    rectangular_shell_lattice,
    rectangular_shell_envelope,
)

spherical_shell_map = mm.spherical_cell_map(
    center=spherical_shell_center,
    inner_radius=shell_inner_radius,
    outer_radius=shell_outer_radius,
    latitude_bounds_degrees=(-75.0, 75.0),
    cells=(16, 10, 2),
)
spherical_shell_lattice = mm.bcc(spherical_shell_map, beam_radius=0.55)
spherical_shell_envelope = pv.Intersection(
    pv.Difference(
        pv.Sphere(spherical_shell_center, shell_outer_radius),
        pv.Sphere(spherical_shell_center, shell_inner_radius),
    ),
    pv.RectPrism.FromMinAndMax(
        pv.Vec3(9.0, 13.0, -slab_half_height),
        pv.Vec3(47.0, 51.0, slab_half_height),
    ),
)
spherical_shell = pv.Intersection(
    spherical_shell_lattice,
    spherical_shell_envelope,
)
shell_comparison = pv.Union(rectangular_shell, spherical_shell)

root = pv.Union(pipe_comparison, shell_comparison)

viz.Render(root)
