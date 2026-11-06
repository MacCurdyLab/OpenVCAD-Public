import numpy as np
import pyvcad as pv
import pyvcad_rendering as viz

# A beam, 100 x 12 x 12 mm, clamped at x = 0
length, half = 100.0, 6.0

# Stand-in for a simulation result: a tetrahedral mesh of the beam with a displacement at every node.
# Each cell of a 20 x 3 x 3 grid is split into six tetrahedra.
nx, ny, nz = 20, 3, 3
xs, ys, zs = np.linspace(0, length, nx + 1), np.linspace(-half, half, ny + 1), np.linspace(-half, half, nz + 1)
points = np.array([(x, y, z) for x in xs for y in ys for z in zs])


def node(i, j, k):
    return (i * (ny + 1) + j) * (nz + 1) + k


cells = []
for i in range(nx):
    for j in range(ny):
        for k in range(nz):
            c = [node(i + a, j + b, k + d) for a, b, d in
                 [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]]
            cells += [[c[0], c[1], c[2], c[6]], [c[0], c[2], c[3], c[6]], [c[0], c[3], c[7], c[6]],
                      [c[0], c[7], c[4], c[6]], [c[0], c[4], c[5], c[6]], [c[0], c[5], c[1], c[6]]]

# A cantilever under a tip load: the axis drops w(x) and each section turns with it, 15 mm at the tip.
tip = 15.0
x, z = points[:, 0], points[:, 2]
w = tip * x**2 * (3 * length - x) / (2 * length**3)
slope = 3 * tip * x * (2 * length - x) / (2 * length**3)
displacement = np.column_stack([z * slope, np.zeros_like(x), -w])

results = pv.UnstructuredFieldDataset.from_tetrahedra(points, np.array(cells))
results.add_point_vector("displacement", displacement, units="mm")

# The part: a beam with a row of holes. It carries the simulation result as its own attribute, which
# Warp.displace() reads by name. Clamping to the mesh boundary covers points just outside the part.
beam = pv.RectPrism(pv.Vec3(length / 2, 0, 0), pv.Vec3(length, 2 * half, 2 * half))
holes = pv.Union(0.0, [pv.Rotate(90, 0, 0, pv.Cylinder(pv.Vec3(x, 0, 0), 3.5, 14.0)) for x in range(10, 100, 10)])
beam = pv.Difference(beam, holes)
beam.set_attribute("displacement", results.vec3_attribute("displacement", outside="boundary_clamp", max_distance=50.0))

bent = pv.Warp.displace("displacement", beam)

# How far each point moved, as a field: soft where it barely moved, stiff where it moved most.
bent.set_attribute(pv.DefaultAttributes.MODULUS, bent.coordinate_field("displacement").map_range(0.0, tip, 100.0, 1000.0))

viz.Render(bent)
