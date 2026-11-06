import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials


def ball(x):
    sphere = pv.Sphere(pv.Vec3(x, 0, 0), 8.0)
    sphere.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,
                         pv.VolumeFractionsAttribute([(1.0, materials.id("blue"))]))
    return sphere


# The same 2 mm wall laid inside, across and outside each sphere's surface.
# Wall outside a sphere is grown material; GrowthPolicy.extend gives it the sphere's material.
inward = pv.Shell(2.0, ball(-20))
centered = pv.Shell(2.0, ball(0), direction=pv.Shell.Direction.centered, growth=pv.GrowthPolicy.extend)
outward = pv.Shell(2.0, ball(20), direction=pv.Shell.Direction.outward, growth=pv.GrowthPolicy.extend)

# Cut the front away to show the walls.
walls = pv.Union(0.0, [inward, centered, outward])
root = pv.Difference(walls, pv.RectPrism(pv.Vec3(0, -15, 0), pv.Vec3(70, 30, 30)))

viz.Render(root, materials)
