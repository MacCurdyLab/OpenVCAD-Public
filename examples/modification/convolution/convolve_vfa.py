import pyvcad as pv
import pyvcad_rendering as viz

# Two adjacent cubes carrying Volume Fraction (material) attributes: the left cube is
# entirely red, the right cube is entirely blue. Convolve blends the material distributions
# across the shared face with a user-specified kernel, producing a smooth multi-material
# transition region. Per-sample fractions are automatically renormalized to sum to 1.
materials = pv.default_materials
attribute = pv.DefaultAttributes.VOLUME_FRACTIONS

left_side = pv.RectPrism.FromMinAndMax(pv.Vec3(-10.0, -10.0, -10.0), pv.Vec3(0.0, 10.0, 10.0))
right_side = pv.RectPrism.FromMinAndMax(pv.Vec3(0.0, -10.0, -10.0), pv.Vec3(10.0, 10.0, 10.0))
left_side.set_attribute(attribute, pv.VolumeFractionsAttribute([(1.0, materials.id("red"))]))
right_side.set_attribute(attribute, pv.VolumeFractionsAttribute([(1.0, materials.id("blue"))]))
combined = pv.Union(left_side, right_side)

# BoxKernel(2) is a 5x5x5 uniform average. The physical_radius spans 8mm along each axis
# ((2*2 + 1) * step; step = physical_radius / radius = 1mm here). During prepare(), the
# child's VF attributes are precomputed onto a dense voxel grid so the per-sample kernel
# loop only does trilinear reads.
kernel = pv.BoxKernel(2)
smoothed = pv.Convolve(combined, [attribute], kernel, [2.0, 2.0, 2.0], override_voxel_size=[0.25, 0.25, 0.25])

viz.Render(smoothed, pv.default_materials)
