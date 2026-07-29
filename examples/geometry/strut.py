"""
Strut Demo - A single cylindrical rod running between two points.

GraphLattice builds each of its unit cells out of many Struts internally
(see examples/geometry/graph_lattice.py); this example uses Strut directly,
wiring up a simple tetrahedral wireframe by hand from six edges.
"""
import pyvcad as pv
import pyvcad_rendering as viz

radius = 0.5  # mm

v0 = pv.Vec3(0.0, 0.0, 6.0)
v1 = pv.Vec3(6.0, 0.0, -3.0)
v2 = pv.Vec3(-3.0, 5.2, -3.0)
v3 = pv.Vec3(-3.0, -5.2, -3.0)

edges = [(v0, v1), (v0, v2), (v0, v3), (v1, v2), (v2, v3), (v3, v1)]
struts = [pv.Strut(start, end, radius) for start, end in edges]

root = struts[0]
for strut in struts[1:]:
    root = pv.Union(root, strut)

viz.Render(root)
