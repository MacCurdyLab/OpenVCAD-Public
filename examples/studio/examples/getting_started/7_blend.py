import pyvcad as pv

materials = pv.default_materials()

part_a = pv.CAD(pv.resources_path() + "examples/data/3d_models/card_left.step", True, materials.id("red"))
part_b = pv.CAD(pv.resources_path() + "examples/data/3d_models/card_right.step", True, materials.id("blue"))
# Convolution requires a single child so combine each object
union = pv.Union(False, [part_a, part_b]) 

root = pv.Blend(10, union)