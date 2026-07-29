import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# Crossing rectangular prisms
cube_x = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(20, 6, 6))
cube_y = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(6, 20, 6))

# Horizontal prism is 100% blue
frac_blue = pv.VolumeFractionsAttribute([("1.0", materials.id("blue"))])
cube_x.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, frac_blue)

# Vertical prism is 100% red
frac_red = pv.VolumeFractionsAttribute([("1.0", materials.id("red"))])
cube_y.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, frac_red)

root = pv.Union(cube_x, cube_y)

# The AverageConflictResolver automatically handles normalized material distributions.
# Where the cubes intersect, it will average the distributions and re-normalize,
# creating a perfect 50/50 mix of Red and Blue material.
root.set_attribute_conflict_resolver(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.resolvers.AverageConflictResolver())

viz.Render(root, materials)
