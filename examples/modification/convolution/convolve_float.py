import pyvcad as pv
import pyvcad_rendering as viz

# Two adjacent cubes sharing the X=0 face, each with a different density value. Convolve
# applies a user-specified kernel to smooth/blur/sharpen the attribute across the boundary
# without touching geometry. Under the hood, prepare() precomputes the child's attributes
# onto a dense voxel grid so each kernel tap at sample time is a cheap trilinear lookup
# instead of a full child-tree traversal.
attribute = pv.DefaultAttributes.DENSITY

left_box = pv.RectPrism.FromMinAndMax(pv.Vec3(-15.0, -15.0, -15.0), pv.Vec3(0.0, 15.0, 15.0))
left_box.set_attribute(attribute, pv.FloatAttribute(0.0))
right_box = pv.RectPrism.FromMinAndMax(pv.Vec3(0.0, -15.0, -15.0), pv.Vec3(15.0, 15.0, 15.0))
right_box.set_attribute(attribute, pv.FloatAttribute(1.0))
combined = pv.Union(left_box, right_box)

# Convolve is the generic sibling of Blend: use it for arbitrary kernels (custom weights,
# sharpening, derivatives). For the common box-blend case, pv.Blend is shorthand and has a
# faster O(1)-per-sample path.
kernel = pv.BoxKernel(6)
smoothed = pv.Convolve(combined, [attribute], kernel, [2.0, 2.0, 2.0], override_voxel_size=[0.25, 0.25, 0.25])

viz.Render(smoothed)
