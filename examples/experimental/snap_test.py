import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials


sphere = pv.Sphere(pv.Vec3(0,0,0), 10, materials.id("red"))

sample_point = pv.Vec3(15, 0, 0)
sample_point_sdf = sphere.evaluate(sample_point.x, sample_point.y, sample_point.z)
sample_point_normal = sphere.gradient(sample_point)

snapped_point = sphere.snap(sample_point)
snapped_point_sdf = sphere.evaluate(snapped_point.x, snapped_point.y, snapped_point.z)
snapped_normal = sphere.gradient(snapped_point)

print(f"Sampled Point: ({sample_point.x}, {sample_point.y}, {sample_point.z}) with distance {sample_point_sdf} mm from the surface and normal ({sample_point_normal.x}, {sample_point_normal.y}, {sample_point_normal.z}).")
print(f"Snapped Point: ({snapped_point.x}, {snapped_point.y}, {snapped_point.z}) with distance {snapped_point_sdf} mm from the surface and normal ({snapped_normal.x}, {snapped_normal.y}, {snapped_normal.z}).")