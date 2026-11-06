import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials


def coloured(node, colour):
    node.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,
                       pv.VolumeFractionsAttribute([(1.0, materials.id(colour))]))
    return node


# A peg and the block it slides into.
peg = coloured(pv.Cylinder(pv.Vec3(0, 0, 4), 4.0, 16.0), "red")
block = coloured(pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(24, 24, 12)), "blue")

# Cut the block around the peg, leaving 1 mm of clearance all round, with a small chamfer on the
# hole's rim. The gap could also be a field, for example looser at the top than at the bottom.
socket = pv.Difference.clearance(block, peg, 1.0, blend_radius=1.5, profile=pv.BlendProfile.chamfer)

# Show the socket cut in half, with the peg seated in it.
half = pv.Difference(socket, pv.RectPrism(pv.Vec3(0, -15, 0), pv.Vec3(40, 30, 40)))
root = pv.Union(half, pv.Difference(peg, pv.RectPrism(pv.Vec3(0, -15, 0), pv.Vec3(40, 30, 40))))

viz.Render(root, materials)
