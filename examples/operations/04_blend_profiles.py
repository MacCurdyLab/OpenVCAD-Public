import pyvcad as pv
import pyvcad_rendering as viz

# The same joint, a post standing on a plate, blended with each profile in turn. The radius means the
# same dip for quadratic and cubic (their fillets reach about 4r and 6r along each face), and the
# true arc radius or bevel size for circular and chamfer.
profiles = [pv.BlendProfile.quadratic, pv.BlendProfile.circular, pv.BlendProfile.chamfer, pv.BlendProfile.cubic]

joints = []
for index, profile in enumerate(profiles):
    x = (index - 1.5) * 26.0
    plate = pv.RectPrism(pv.Vec3(x, 0, 0), pv.Vec3(22, 22, 3))
    post = pv.Cylinder(pv.Vec3(x, 0, 6.5), 3.0, 10.0)
    # A blend radius of 1.5 mm rounds (or bevels) the seam where the post meets the plate.
    joints.append(pv.Union([plate, post], blend_radius=1.5, profile=profile))

root = pv.Union(joints)

viz.Render(root)
