import pyvcad as pv
import pyvcad_rendering as viz


def strut_chain(points, radius):
    """Thin struts joining consecutive points: a quick way to look at a curve."""
    struts = [pv.Strut(pv.Vec3(*a), pv.Vec3(*b), radius) for a, b in zip(points[:-1], points[1:])]
    return pv.BBoxUnion(struts)


# Five kinds of curve. Points can be tuples, lists, Vec3 or NumPy arrays; 2D points get z = 0.
curves = [
    pv.LineSegment((0, 0, 0), (0, 0, 24)),
    pv.ArcCurve((16, 0, 12), 9.0, -90.0, 180.0, normal=(0, 1, 0)),
    pv.BezierCurve([(32, 0, 0), (32, 18, 6), (46, -18, 18), (46, 0, 24)]),
    pv.BSplineCurve.interpolate([(60, 0, 0), (68, 7, 6), (60, 14, 12), (52, 7, 18), (60, 0, 24)]),
    pv.CompositeCurve([
        pv.LineSegment((76, 0, 0), (76, 0, 14)),
        pv.ArcCurve((81, 0, 14), 5.0, 180.0, 0.0, normal=(0, -1, 0)),
        pv.LineSegment((86, 0, 14), (86, 0, 6)),
    ]),
]

# Sample each curve evenly in arc length and draw it.
parts = [strut_chain(curve.sample(60), 0.6) for curve in curves]

# Rotation-minimizing frames on the B-spline: short ribs along each frame's normal.
spline = curves[3]
frames = spline.frames(14)
for origin, normal in zip(frames["origins"], frames["normals"]):
    parts.append(pv.Strut(pv.Vec3(*origin), pv.Vec3(*(origin + 3.5 * normal)), 0.35))

root = pv.BBoxUnion(parts)

viz.Render(root)
