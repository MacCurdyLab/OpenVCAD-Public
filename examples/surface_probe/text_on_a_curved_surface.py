import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# The part: a pressure-vessel body, a cylindrical barrel capped by a dome. Neither the
# barrel wall nor the dome is axis aligned where we want to mark it, which is exactly the
# case where guessing pitch/yaw/roll by hand falls apart.
barrel_radius = 28.0
barrel_height = 60.0
body = pv.Union(
    pv.Cylinder(pv.Vec3(0, 0, 0), barrel_radius, barrel_height),
    pv.Sphere(pv.Vec3(0, 0, barrel_height / 2.0), barrel_radius),
)
body.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute([(1.0, materials.id("blue"))]),
)

# prepare() has to run before any probe: evaluate() and gradient() are undefined until it
# has, and the probe is built on both.
body.prepare(pv.Vec3(0.25, 0.25, 0.25), 1.0)

# probe_point takes a rough point, of the kind you read off the renderer's Probe tool. It
# does not have to sit exactly on the surface: the probe walks it down onto the real field
# and reports where it landed plus the outward unit normal there.
dome_probe = pv.probe_point(body, pv.Vec3(19.0, 11.0, 44.0))

# probe_ray is the other way in, and it is what a viewport pick maps onto: shoot a ray at
# the part and it reports the first surface the ray enters. This one comes in horizontally
# at the barrel wall.
barrel_probe = pv.probe_ray(body, pv.Vec3(200.0, 136.0, -10.0), pv.Vec3(-1.0, -0.68, 0.0))

for name, probe in (("dome", dome_probe), ("barrel", barrel_probe)):
    print("{:7} hit={}  position {:.3f}, {:.3f}, {:.3f}  normal {:.3f}, {:.3f}, {:.3f}".format(
        name, probe.hit,
        probe.position.x, probe.position.y, probe.position.z,
        probe.normal.x, probe.normal.y, probe.normal.z))


def place_text_on_surface(text, probe, sink_depth, up=pv.Vec3(0, 0, 1)):
    """Stand a Text node up against the probed surface point.

    alignment_angles turns the normal into the pitch/yaw/roll that pv.Rotate wants: it aims
    the node's local +Z along the normal and its local +Y along the second argument. Text
    extrudes along +Z, so that lays the glyphs flat on the surface with the extrusion
    pointing straight out of it.

    `up` is where you want the text to read as upright. It gets negated on the way in
    because the Text node builds its glyphs on a flipped X axis, which leaves their visual
    up along the node's own -Y rather than +Y.

    `sink_depth` is how far the text's back face sits below the surface: sink it most of
    the way and Union leaves a raised mark, sink it halfway and Difference cuts an engraved
    one. Sink deeper than the surface curves away over the width of the text, or the ends
    of the word will float off (or bury themselves in) a strongly curved face.
    """
    # Rotate pivots on its child's bounding box centre, so centre the node on the origin
    # first and the rotation stays about a point we control.
    box_min, box_max = text.bounding_box()
    centred = pv.Translate(
        -(box_min.x + box_max.x) / 2.0,
        -(box_min.y + box_max.y) / 2.0,
        -(box_min.z + box_max.z) / 2.0,
        text,
    )
    glyph_up = pv.Vec3(-up.x, -up.y, -up.z)
    aimed = pv.Rotate(pv.alignment_angles(probe.normal, glyph_up), centred)

    lift = (box_max.z - box_min.z) / 2.0 - sink_depth
    return pv.Translate(
        probe.position.x + probe.normal.x * lift,
        probe.position.y + probe.normal.y * lift,
        probe.position.z + probe.normal.z * lift,
        aimed,
    )


# A raised badge on the dome, and an engraved serial number on the barrel wall.
badge_depth = 6.0
badge = pv.Text("VCAD", 8.0, badge_depth, pv.FontAspect.Bold)
badge.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute([(1.0, materials.id("yellow"))]),
)

serial = pv.Text("SN-42", 7.0, 8.0)

root = pv.Difference(
    pv.Union(body, place_text_on_surface(badge, dome_probe, badge_depth / 2.0)),
    place_text_on_surface(serial, barrel_probe, 5.0),
)

viz.Render(root, materials)
