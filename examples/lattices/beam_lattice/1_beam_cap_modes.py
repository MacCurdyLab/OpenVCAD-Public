"""
Beam cap modes - the three ways a strut end is closed off.

Strut sweeps a conical frustum between two points, with an independent radius
and cap mode at each end. The cap mode decides what closes that end:

  CapMode.Butt        flat, leaving a bare cone or cylinder
  CapMode.Sphere      a full sphere of the end radius, which can bulge past a
                      narrowing lateral surface
  CapMode.HemiSphere  only the outward half of that sphere, flush with the end

These are the same three modes the 3MF Beam Lattice Extension defines. On a
cylinder, where both radii match, sphere and hemisphere describe the same solid;
the difference only shows up on a cone, at its wider end.
"""
import pyvcad as pv
import pyvcad_rendering as viz

small_radius = 2.0  # mm
large_radius = 5.0  # mm
height = 20.0       # mm
spacing = 14.0      # mm

modes = [pv.CapMode.Butt, pv.CapMode.Sphere, pv.CapMode.HemiSphere]

cones = []
for index, mode in enumerate(modes):
    x = (index - 1) * spacing
    cones.append(
        pv.Strut(
            pv.Vec3(x, 0.0, 0.0),
            pv.Vec3(x, 0.0, height),
            small_radius,
            large_radius,
            mode,
            mode,
        )
    )

root = cones[0]
for cone in cones[1:]:
    root = pv.Union(root, cone)

viz.Render(root)
