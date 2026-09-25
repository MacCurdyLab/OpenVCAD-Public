"""Fill an inkjet support volume with a gyroid micro-lattice."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

materials = pv.default_materials
voxel_size = pv.Vec3(0.4, 0.4, 0.4)

stem = pv.RectPrism(pv.Vec3(0.0, 0.0, 9.0), pv.Vec3(6.0, 6.0, 18.0))
bar = pv.RectPrism(pv.Vec3(0.0, 0.0, 21.0), pv.Vec3(28.0, 6.0, 6.0))
part = pv.Union(stem, bar)

analyzer = pv.SupportAnalyzer(part, voxel_size)
support_volume = analyzer.analyze()

# Tile a gyroid through the support bounds, then clip it to the support solid.
# No conformal mapping is needed; this is an ordinary rectangular fill.
bbox_min, bbox_max = support_volume.bounding_box()
lattice_support = pv.Intersection(
    mm.gyroid(
        mm.rectangular_cell_map(
            (bbox_min, bbox_max),
            cell_size=pv.Vec3(5.0, 5.0, 5.0),
        ),
        wall_thickness=0.7,
    ),
    support_volume,
)

part.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute([(1.0, materials.id("white"))]),
)
lattice_support.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute([(1.0, materials.id("cyan"))]),
)

root = pv.Union(part, lattice_support)
viz.Render(root, materials)
