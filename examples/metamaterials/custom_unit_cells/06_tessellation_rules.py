import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

# A space-filling tessellation plus a rule makes a graph cell. The tetrahedral-octahedral
# honeycomb under four rules, left to right: its edges (the octet truss), each cell's centre
# joined to its corners, each face's centre joined to its corners, and the dual (the centres of
# neighbouring cells joined).
tet_oct = mm.tessellation("tet_oct")
rules = ["edges", "cell_vertex_centroid", "facet_vertex_centroid", "dual"]

lattices = []
for index, rule in enumerate(rules):
    x = 28.0 * index
    cell_map = mm.rectangular_cell_map((pv.Vec3(x - 10, -10, -10), pv.Vec3(x + 10, 10, 10)),
                                       cells=(2, 2, 2))
    lattices.append(mm.graph_lattice(cell_map, tet_oct.edges(rule), beam_radius=0.45))

# The side faces of a prism tessellation are walls: a triangular honeycomb as a face cell. Its
# design proportions come with the tessellation.
triangles = mm.tessellation("triangular_prism")
u, v, w = triangles.cell_size
wall_map = mm.rectangular_cell_map((pv.Vec3(102, -10, -10), pv.Vec3(102 + 3 * 20 * u / v, 10, 10)),
                                   cells=(3, 2, 2))
lattices.append(mm.face_lattice(wall_map, triangles.face_cell(face_tags="side"), wall_thickness=0.6))

root = pv.Union(0.0, lattices)
viz.Render(root)
