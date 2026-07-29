"""Assign materials to reusable strut selections without expanding repeated nodes."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

materials = pv.default_materials
vertices = [
    pv.Vec3(0.0, 0.0, 0.0), pv.Vec3(1.0, 0.0, 0.0),
    pv.Vec3(0.0, 1.0, 0.0), pv.Vec3(1.0, 1.0, 0.0),
    pv.Vec3(0.0, 0.0, 1.0), pv.Vec3(1.0, 0.0, 1.0),
    pv.Vec3(0.0, 1.0, 1.0), pv.Vec3(1.0, 1.0, 1.0),
]
edges = [
    (0, 1), (0, 2), (1, 3), (2, 3),
    (4, 5), (4, 6), (5, 7), (6, 7),
    (0, 4), (1, 5), (2, 6), (3, 7),
]
edge_tags = [1] * 8 + [2] * 4
unit_cell = pv.GraphUnitCell(vertices, edges, edge_tags=edge_tags)
cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-15.0, -15.0, -15.0), pv.Vec3(15.0, 15.0, 15.0)),
    cells=(3, 3, 3),
)
root = mm.graph_lattice(cell_map, unit_cell, beam_radius=1.0)
root.struts.with_tag(1).set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute([(1.0, materials.id("blue"))]),
)
root.struts.with_tag(2).set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute([(1.0, materials.id("white"))]),
)
viz.Render(root, materials)
