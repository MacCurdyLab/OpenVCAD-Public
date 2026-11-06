import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

# A beam lattice straight from the cells of a mesh, with the same rules as the tessellation
# builders. No cell map is needed, so the struts follow any shape the mesher can fill.
def shape():
    return pv.Union(pv.Sphere(pv.Vec3(0.0, 0.0, 0.0), 14.0), pv.Sphere(pv.Vec3(0.0, 0.0, 16.0), 9.0))


body = shape()

# Left: the edges of a tetrahedral mesh, struts thicker towards the bottom.
settings = pv.TetrahedralMeshFixedSettings()
settings.cell_size = 5.0
settings.facet_size = 5.0
settings.facet_distance = 0.5
tets = pv.TetrahedralMesh.from_tree(body, settings)
tet_struts = mm.mesh_lattice(tets, "edges", beam_radius=lambda x, y, z, d: 0.7 - 0.012 * z)

# Middle: the dual of the surface triangles, a cell-like net on the skin. Remeshing first gives
# even 4 mm triangles, so the net's cells are even too.
surface = pv.SurfaceMesh(body, 0.5).remeshed(4.0)
skin_net = mm.mesh_lattice(surface, "dual", beam_radius=0.5)

# Right: each voxel of a hexahedral mesh joined from its centre to its corners (BCC in voxels).
hex_settings = pv.HexahedralMeshSettings()
hex_settings.voxel_size = pv.Vec3(5.0, 5.0, 5.0)
hexes = pv.HexahedralMesh.from_tree(body, hex_settings)
voxel_bcc = mm.mesh_lattice(hexes, "cell_vertex_centroid", beam_radius=0.5)

# Struts are centred on the mesh, so trim the ones on the skin back to the body.
root = pv.Union([
    pv.Translate(-36.0, 0.0, 0.0, pv.Intersection(tet_struts, shape())),
    skin_net,
    pv.Translate(36.0, 0.0, 0.0, pv.Intersection(voxel_bcc, shape())),
])

viz.Render(root)
