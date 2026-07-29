import pyvcad as pv
import pyvcad_rendering as viz

# Two adjacent cubes with different vec4 (RGBA) colors. Convolve smooths the color
# transition across their shared face with an arbitrary kernel. Geometry is unaffected.
# During prepare() the child's attributes are parallel-sampled onto a dense voxel grid
# so that per-sample kernel taps reduce to cheap trilinear lookups.
attribute = pv.DefaultAttributes.COLOR_RGBA

box = pv.RectPrism.FromMinAndMax(pv.Vec3(-15.0, -15.0, -15.0), pv.Vec3(0.0, 15.0, 15.0))
box.set_attribute(attribute, pv.Vec4Attribute(1.0, 0.0, 0.0, 1.0))
box2 = pv.RectPrism.FromMinAndMax(pv.Vec3(0.0, -15.0, -15.0), pv.Vec3(15.0, 15.0, 15.0))
box2.set_attribute(attribute, pv.Vec4Attribute(0.0, 1.0, 0.0, 1.0))
combined = pv.Union(box, box2)

# Kernel size is (2r + 1)^3, so BoxKernel(2) is a 5x5x5 averaging kernel.
kernel = pv.BoxKernel(2)
smoothed = pv.Convolve(combined, [attribute], kernel, [2.0, 2.0, 2.0], override_voxel_size=[0.25, 0.25, 0.25])

viz.Render(smoothed)
