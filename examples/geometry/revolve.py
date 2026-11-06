"""
Revolve Demo - Spin a 2D Profile about the Z axis.

Revolve reads the profile's x as the distance from the Z axis and its y as
the height. A full 360 degree revolve closes into a solid of revolution; a
smaller angle leaves flat caps, which is handy for showing a cross-section.
(PolygonRevolve does the same from a list of 3D points and any axis.)
"""
import pyvcad as pv
import pyvcad_rendering as viz

# Half-section of a cup: the edge on x=0 lies on the axis and fills the base.
cup_profile = pv.Profile.polygon([(0, 0), (12, 0), (15, 20), (13.5, 20), (10.5, 2), (0, 2)])
cup = pv.Revolve(cup_profile)

# The same profile swept only 270 degrees, so the wall section is visible.
cutaway = pv.Revolve(cup_profile, 270.0)

root = pv.Union(cup, pv.Translate(40.0, 0.0, 0.0, cutaway))

viz.Render(root)
