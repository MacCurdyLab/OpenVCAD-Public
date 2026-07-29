import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
attribute = pv.DefaultAttributes.VOLUME_FRACTIONS

# Two adjacent cubes with different pure-material distributions. pv.Blend mixes the volume
# fractions smoothly across the shared face; material fractions are renormalized to sum to 1.
left_side = pv.RectPrism.FromMinAndMax(pv.Vec3(-10.0, -10.0, -10.0), pv.Vec3(0.0, 10.0, 10.0))
right_side = pv.RectPrism.FromMinAndMax(pv.Vec3(0.0, -10.0, -10.0), pv.Vec3(10.0, 10.0, 10.0))
left_side.set_attribute(attribute, pv.VolumeFractionsAttribute([(1.0, materials.id("red"))]))
right_side.set_attribute(attribute, pv.VolumeFractionsAttribute([(1.0, materials.id("blue"))]))
combined = pv.Union(left_side, right_side)

# override_voxel_size lets you fall back to a coarser internal grid if memory is a concern on
# large scenes. Trilinear interpolation keeps the visible output smooth.
smoothed = pv.Blend(combined, [attribute], [2.0, 2.0, 2.0], num_passes=4, override_voxel_size=[0.25,0.25,0.25])

viz.Render(smoothed, pv.default_materials)
