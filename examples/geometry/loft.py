"""
Loft Demo - Blend between 2D Profiles placed at heights.

Loft blends the sections' signed distances, so sections can differ in shape
and topology. smooth=True (the default) passes smoothly through every section;
smooth=False blends straight from one section to the next.
"""
import pyvcad as pv
import pyvcad_rendering as viz

# A duct that turns from a circle into a rounded rectangle and back into a smaller circle.
duct = pv.Loft([pv.Profile.circle(12.0), pv.Profile.rounded_rectangle(30.0, 18.0, 4.0), pv.Profile.circle(7.0)],
               [0.0, 30.0, 60.0])

# One disc that splits into two legs: the sections need not have the same number of loops.
legs = pv.Profile.circle(5.0, center=(-7.0, 0.0)) | pv.Profile.circle(5.0, center=(7.0, 0.0))
split = pv.Loft([pv.Profile.circle(12.0), legs], [0.0, 60.0], smooth=False)

root = pv.Union([duct, pv.Translate(45.0, 0.0, 0.0, split)])

viz.Render(root)
