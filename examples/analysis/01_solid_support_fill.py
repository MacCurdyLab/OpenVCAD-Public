"""Compute an inkjet support volume and fill it with support material."""

import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
voxel_size = pv.Vec3(0.4, 0.4, 0.4)

# A T-bracket has a clear downward-facing volume under each arm of the crossbar.
stem = pv.RectPrism(pv.Vec3(0.0, 0.0, 9.0), pv.Vec3(6.0, 6.0, 18.0))
bar = pv.RectPrism(pv.Vec3(0.0, 0.0, 21.0), pv.Vec3(28.0, 6.0, 6.0))
part = pv.Union(stem, bar)

# SupportAnalyzer samples the part layer-by-layer and returns the unsupported
# volume as an ordinary OpenVCAD implicit solid.
analyzer = pv.SupportAnalyzer(part, voxel_size)
support_volume = analyzer.analyze()

part.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute([(1.0, materials.id("white"))]),
)
support_volume.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute([(1.0, materials.id("cyan"))]),
)

root = pv.Union(part, support_volume)
viz.Render(root, materials)
