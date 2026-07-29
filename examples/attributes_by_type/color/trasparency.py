import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_compilers as pvc

render = False
export = True

transparency_steps = [0.0, 0.01, 0.03, 0.05, 0.1, 0.2, 0.4]
colors_to_test = [pv.Vec3(1,1,1), pv.Vec3(1,0,0), pv.Vec3(0,1,0), pv.Vec3(0,0,1)]
spacing = 2
overall_size = 25

voxel_size = pv.Vec3(0.0423,0.0846,0.027)
output_dir = "output/transparency_tests/"
prefix = "test_"

def make_transparency_test(object, transparency = 0.01, transparency_color = pv.Vec3(1,1,1), object_color = pv.Vec4(1,1,0,1), overall_size=30, bbox_extra=20):
    transparency_color_vec4 = pv.Vec4(transparency_color.x, transparency_color.y, transparency_color.z, transparency)

    text_size = 10

    wrapper = pv.BBoxUnion([object])
    wrapper.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(object_color.r, object_color.g, object_color.b, object_color.a))

    mesh_bbox_min, mesh_bbox_max = wrapper.bounding_box()
    mesh_size = pv.Vec3(mesh_bbox_max.x - mesh_bbox_min.x, mesh_bbox_max.y - mesh_bbox_min.y, mesh_bbox_max.z - mesh_bbox_min.z)

    box = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(mesh_size.x + bbox_extra, mesh_size.y + bbox_extra, mesh_size.z + bbox_extra))
    box.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(transparency_color_vec4.r, transparency_color_vec4.g, transparency_color_vec4.b, transparency_color_vec4.a))

    # Add box with text in it to the bottom of the other box
    text_box = pv.RectPrism(pv.Vec3(0, 0, -mesh_size.z/2 - bbox_extra/2 - text_size/2),
                            pv.Vec3(mesh_size.x + bbox_extra, mesh_size.y + bbox_extra, text_size))
    text_box.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(1,1,1,1)) # Pure white box
    text_depth = text_size / 4
    text_front = pv.Text(f"T: {round(transparency * 100.0)}% | D: {bbox_extra} mm", height=text_size - 2, depth=text_depth)
    text_front = pv.Rotate(90, 0, 0, text_front)
    text_front = pv.Translate(0, mesh_size.y/2 + bbox_extra/2 - text_depth/2, -mesh_size.z/2 - bbox_extra/2 - text_size/2 + 0.1, text_front)

    def fmt(v):
        return f"{v:.2f}".rstrip("0").rstrip(".")
    text_back = pv.Text(f"({fmt(transparency_color_vec4.r)},{fmt(transparency_color_vec4.g)},{fmt(transparency_color_vec4.b)},{fmt(transparency_color_vec4.a)})", height=text_size-3, depth=text_depth)
    text_back = pv.Rotate(90, 0, 0, text_back)
    text_back = pv.Rotate(0, 0, 180, text_back)
    text_back = pv.Translate(0, -mesh_size.y/2 - bbox_extra/2 + text_depth/2, -mesh_size.z/2 - bbox_extra/2 - text_size/2 + 0.1, text_back)

    text_union = pv.Union(text_front, text_back)
    text_union.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(0,0,0,1)) # Pure black text
    text_box = pv.Union(text_union, text_box)
    union = pv.BBoxUnion([text_box, wrapper, box])

    combined_bbox_min, combined_bbox_max = union.bounding_box()
    combined_size = pv.Vec3(combined_bbox_max.x - combined_bbox_min.x, combined_bbox_max.y - combined_bbox_min.y, combined_bbox_max.z - combined_bbox_min.z)
    scale_factor = overall_size / max(combined_size.x, combined_size.y, combined_size.z)

    root = pv.Scale(scale_factor, union)
    return root

mesh_path = "../../data/3d_models/3DBenchy.3mf"
object = pv.Mesh(mesh_path, center=True)

union = pv.BBoxUnion()
for color in colors_to_test:
    for i, t in enumerate(transparency_steps):
        test_obj = make_transparency_test(object, transparency=t, transparency_color=color, overall_size=overall_size)
        bbox_min, bbox_max = test_obj.bounding_box()
        x_size = bbox_max.x - bbox_min.x
        y_size = bbox_max.y - bbox_min.y
        translation = pv.Translate((x_size + spacing) * i, (y_size + spacing) * colors_to_test.index(color), 0, test_obj)
        union.add_child(translation)

root = union

if render:
    viz.Render(root)

if export:
    import shutil, os
    if export and os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    #Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    compiler = pvc.ColorInkjetCompiler(root, voxel_size, output_dir, prefix)

    def print_progress(progress):
        print(f"Compilation progress: {progress*100:.2f}%")

    compiler.set_progress_callback(print_progress)
    compiler.compile()
