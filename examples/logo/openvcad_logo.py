"""
OpenVCAD logo: "Curved Stack V".

Five V ribbons whose arms bow gently inward into a round bottom are stacked in
depth and nested inward, like the original OpenVCAD logo but with flowing arms
instead of straight ones. Every layer carries the same amber -> violet -> cyan
COLOR_RGBA sweep across its width, pulled toward a dark plum the further back
it sits. The layers overlap slightly in depth, so the stack is one fused solid
that can go straight to a color inkjet printer.

Each layer is a single implicit Function: the V centreline is two circular arcs
(one per arm, folded onto each other with |x|) that meet a smaller fillet arc at
the bottom, and the ribbon is a rounded rectangle swept along that path. Using
exact circle distances keeps the bottom a true round and the arms free of any
mitre seam.
"""
import math

import pyvcad as pv
import pyvcad_rendering as viz

tip_y = 30.0
bottom_y = -22.0
half_span = 27.0
fillet_radius = 6.0
arm_radius = 140.0       # large radius: a gentle inward bow
ribbon_width = 10.0
ribbon_thickness = 3.0
corner_radius = 1.2
layers = 5
layer_spacing = 2.9      # depth step between layers; a hair under the thickness fuses them
layer_lift = 6.5         # each layer's bottom moves up by this much
layer_inset = 2.6        # and its tips move inward by this much

# Sweep across each layer; deeper layers are blended toward the dark tone
left_color = (1.00, 0.62, 0.12)
mid_color = (0.60, 0.15, 0.65)
right_color = (0.12, 0.70, 0.95)
back_tone = (0.10, 0.05, 0.25)


def arc_terms(name, cx, cy, radius, ref, direction, s0):
    """exprtk lines for one arc: c<name> is the signed offset from the arc (positive toward
    the inside of the V) and s<name> is the path length measured from the arc's start."""
    return f"""
var dx{name} := xa - ({cx});
var dy{name} := y - ({cy});
var r{name} := sqrt(dx{name} * dx{name} + dy{name} * dy{name});
var c{name} := {radius} - r{name};
var s{name} := {s0} + {radius * direction} * atan2({ref[0]} * dy{name} - {ref[1]} * dx{name}, {ref[0]} * dx{name} + {ref[1]} * dy{name});
"""


def piece_sdf(name, cap_expr, hw, hh, radius):
    """Rounded-rectangle distance for one path piece, capped along the path by cap_expr."""
    return f"""
var qx{name} := abs(c{name}) - {hw};
var qz{name} := abs(zz) - {hh};
var qy{name} := {cap_expr};
var d{name} := sqrt(max(qx{name}, 0)^2 + max(qy{name}, 0)^2 + max(qz{name}, 0)^2) + min(max(qx{name}, max(qy{name}, qz{name})), 0) - {radius};
"""


def v_ribbon(half_span, tip_y, bottom_y, fillet_radius, arm_radius, width, thickness, corner_radius, z_offset):
    """One implicit V ribbon: arms that bow inward on circles of `arm_radius`, joined by a
    fillet arc of `fillet_radius` at the bottom, with a rounded rectangular cross-section."""
    hw = width / 2.0 - corner_radius
    hh = thickness / 2.0 - corner_radius
    T = (half_span, tip_y)                              # right-arm tip (|x| folds the left arm onto it)
    C = (0.0, bottom_y + fillet_radius)                 # fillet centre
    B = (0.0, bottom_y)                                 # bottom of the V

    # Arm circle centre: distance arm_radius from the tip and internally tangent to the fillet
    dist = arm_radius - fillet_radius
    ex, ey = T[0] - C[0], T[1] - C[1]
    d = math.hypot(ex, ey)
    along = (dist * dist - arm_radius * arm_radius + d * d) / (2.0 * d)
    across = math.sqrt(max(dist * dist - along * along, 0.0))
    mx, my = C[0] + along * ex / d, C[1] + along * ey / d
    Ca = min(((mx - across * ey / d, my + across * ex / d), (mx + across * ey / d, my - across * ex / d)), key=lambda p: p[0])

    # Tangent point where the arm arc hands over to the fillet arc
    gx, gy = C[0] - Ca[0], C[1] - Ca[1]
    g = math.hypot(gx, gy)
    P = (Ca[0] + arm_radius * gx / g, Ca[1] + arm_radius * gy / g)

    # Arc lengths and sweep directions, from the tip down to the bottom
    vT = (T[0] - Ca[0], T[1] - Ca[1])
    vP_arm = (P[0] - Ca[0], P[1] - Ca[1])
    cross_arm = vT[0] * vP_arm[1] - vT[1] * vP_arm[0]
    arm_length = arm_radius * abs(math.atan2(cross_arm, vT[0] * vP_arm[0] + vT[1] * vP_arm[1]))
    vP = (P[0] - C[0], P[1] - C[1])
    vB = (B[0] - C[0], B[1] - C[1])
    cross_fillet = vP[0] * vB[1] - vP[1] * vB[0]

    expr = f"""
var xa := abs(x);
var zz := z - ({z_offset});
{arc_terms("a", Ca[0], Ca[1], arm_radius, vT, 1.0 if cross_arm > 0 else -1.0, 0.0)}
{arc_terms("f", C[0], C[1], fillet_radius, vP, 1.0 if cross_fillet > 0 else -1.0, arm_length)}
{piece_sdf("a", f"max(-sa, sa - {arm_length})", hw, hh, corner_radius)}
{piece_sdf("f", f"{arm_length} - sf", hw, hh, corner_radius)}
min(da, df)
"""
    m = width + 2.0
    return pv.Function(expr, pv.Vec3(-half_span - m, bottom_y - m, z_offset - m), pv.Vec3(half_span + m, tip_y + m, z_offset + m))


def sweep(x_min, x_max, c0, c1, c2):
    """COLOR_RGBA that blends through three stops across x."""
    t = f"clamp((x - ({x_min})) / ({x_max - x_min}), 0, 1)"
    w0 = f"clamp(1 - 2*{t}, 0, 1)"
    w2 = f"clamp(2*{t} - 1, 0, 1)"
    w1 = f"(1 - {w0} - {w2})"
    channel = lambda i: f"{w0}*{c0[i]} + {w1}*{c1[i]} + {w2}*{c2[i]}"
    return pv.Vec4Attribute(channel(0), channel(1), channel(2), "1.0")


def toward(color, tone, f):
    return tuple(color[i] * (1.0 - f) + tone[i] * f for i in range(3))


root = pv.BBoxUnion()
for i in range(layers):
    span_i = half_span - i * layer_inset
    layer = v_ribbon(span_i, tip_y, bottom_y + i * layer_lift, fillet_radius, arm_radius,
                     ribbon_width, ribbon_thickness, corner_radius, -i * layer_spacing)
    f = 0.55 * i / (layers - 1)
    layer.set_attribute(pv.DefaultAttributes.COLOR_RGBA,
                        sweep(-span_i, span_i, toward(left_color, back_tone, f), toward(mid_color, back_tone, f), toward(right_color, back_tone, f)))
    root.add_child(layer)

viz.Render(root)
