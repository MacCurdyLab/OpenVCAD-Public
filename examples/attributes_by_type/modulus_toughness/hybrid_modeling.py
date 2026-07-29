"""
Hybrid attribute modeling on a single J750 dogbone.

The center of the specimen is authored as modulus+toughness design intent,
translated to volume fractions, then combined with directly-authored pure
Vero tabs. pv.Blend smooths the final volume-fraction field across the two
interfaces.
"""
import os

import pyvcad as pv
import pyvcad_attribute_resolver as resolver
import pyvcad_rendering as viz

materials = pv.j750_materials
volume_fractions = pv.DefaultAttributes.VOLUME_FRACTIONS

SOFT_MATERIAL = "VeroMgnt"
RIGID_MATERIAL = "VeroCyan"
LIQUID_MATERIAL = "VeroYellow"

# The tab width controls where the rigid clamp regions end. The remaining
# centered span is the modulus+toughness test region.
tab_region_width = 30.0

target_modulus_mpa = 0.46822539069408137
target_toughness_mj_per_m3 = 0.7299401657003852

blend_radius = [6.0, 6.0, 1.0]
blend_num_passes = 3
blend_voxel_size = [0.5, 0.5, 0.25]

mesh_voxel_size = 0.25
mesh_path = os.path.join(os.path.dirname(__file__), "tensile_ASTM_D412-C.stl")

dogbone_base = pv.Mesh(mesh_path, center=True, override_voxel_size=mesh_voxel_size)
bbox_min, bbox_max = dogbone_base.bounding_box()
object_length = bbox_max.x - bbox_min.x

if tab_region_width <= 0.0:
    raise ValueError("tab_region_width must be positive.")
if 2.0 * tab_region_width >= object_length:
    raise ValueError("tab_region_width leaves no room for the test region.")

left_tab_x_max = bbox_min.x + tab_region_width
right_tab_x_min = bbox_max.x - tab_region_width
test_region_width = right_tab_x_min - left_tab_x_max


def make_region_prism(x_min, x_max):
    return pv.RectPrism.FromMinAndMax(
        pv.Vec3(x_min, bbox_min.y, bbox_min.z),
        pv.Vec3(x_max, bbox_max.y, bbox_max.z),
    )


def clip_dogbone_region(x_min, x_max):
    return pv.Intersection(dogbone_base.clone(), make_region_prism(x_min, x_max))


rigid_material_id = materials.id(RIGID_MATERIAL)
rigid_volume_fractions = pv.VolumeFractionsAttribute([(1.0, rigid_material_id)])

test_region = clip_dogbone_region(left_tab_x_max, right_tab_x_min)
test_region.set_attribute(
    pv.DefaultAttributes.MODULUS,
    pv.FloatAttribute(target_modulus_mpa),
)
test_region.set_attribute(
    pv.DefaultAttributes.TOUGHNESS,
    pv.FloatAttribute(target_toughness_mj_per_m3),
)

resolver.clear_conversions()
resolver.register_j750_modulus_toughness_conversions(
    material_defs=materials,
    rigid_material=RIGID_MATERIAL,
    soft_material=SOFT_MATERIAL,
    liquid_material=LIQUID_MATERIAL,
)
test_region = resolver.adapt(
    test_region,
    [volume_fractions],
    tags=["j750_modulus_toughness"],
)

left_tab_region = clip_dogbone_region(bbox_min.x, left_tab_x_max)
right_tab_region = clip_dogbone_region(right_tab_x_min, bbox_max.x)
left_tab_region.set_attribute(volume_fractions, rigid_volume_fractions)
right_tab_region.set_attribute(volume_fractions, rigid_volume_fractions)

combined = pv.Union()
combined.add_child(left_tab_region)
combined.add_child(test_region)
combined.add_child(right_tab_region)

# root = pv.Blend(
#     combined,
#     [volume_fractions],
#     blend_radius,
#     num_passes=blend_num_passes,
#     override_voxel_size=blend_voxel_size,
# )

root = combined

if volume_fractions not in root.attribute_list():
    raise RuntimeError("The hybrid dogbone is missing volume_fractions.")

viz.Render(root, materials)
