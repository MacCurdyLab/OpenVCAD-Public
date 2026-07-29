import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_compilers as pvc

render = False
export = True
output_dir = "./output"
voxel_size = pv.Vec3(0.0423,0.0846,0.027)
prefix = "swatches_"

materials = pv.default_materials

def make_sample(a_ratio, x_index, y_index):
    v_ratio = 1.0 - a_ratio
    text_height = 3.5
    text_depth = 7
    font = "Consolas"
    font_aspect = pv.FontAspect.Regular
    horizontal_alignment = pv.HorizontalAlignment.Center # Left, Center, Right
    vertical_alignment = pv.VerticalAlignment.Top # Bottom, Center, Top
    text = pv.Text(f"A:{a_ratio*100:.1f}% V:{v_ratio*100:.1f}%", text_height, text_depth, font_aspect, font, horizontal_alignment, vertical_alignment)
    text.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, pv.VolumeFractionsAttribute([f"1.0"], [3]))
    rotated_text = pv.Rotate(0,0,180, text)
    text_translated = pv.Translate(0,-20,0, rotated_text)

    blank = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(30,40,text_depth))
    vfa = pv.VolumeFractionsAttribute([f"{a_ratio}",f"{v_ratio}"], [1,2])
    blank.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, vfa)

    union = pv.Union(text_translated, blank)
    translate = pv.Translate(32*x_index,-42*y_index,0, union)
    return translate

union = pv.BBoxUnion()
union.add_child(make_sample( 0.98, 0,0))
union.add_child(make_sample(0.96, 1,0))
union.add_child(make_sample(0.94, 2,0))
union.add_child(make_sample(0.92, 3,0))
union.add_child(make_sample(0.90, 4,0))
union.add_child(make_sample(0.88, 5,0))
union.add_child(make_sample(0.86, 6,0))
union.add_child(make_sample(0.84, 7,0))
union.add_child(make_sample(0.82, 8,0))
union.add_child(make_sample(0.80, 9,0))

union.add_child(make_sample(0.78, 0,1))
union.add_child(make_sample(0.76, 1,1))
union.add_child(make_sample(0.74, 2,1))
union.add_child(make_sample(0.72, 3,1))
union.add_child(make_sample(0.70, 4,1))
union.add_child(make_sample(0.68, 5,1))
union.add_child(make_sample(0.66, 6,1))
union.add_child(make_sample(0.64, 7,1))
union.add_child(make_sample(0.62, 8,1))
union.add_child(make_sample(0.60, 9,1))

root = union

if render:
    viz.Render(root, pv.default_materials)

if export:
    print(f"Output Directory: {output_dir}")

    # Delete the output directory if it already exists
    import shutil, os
    if export and os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    #Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    compiler = pvc.MaterialInkjetCompiler(root, voxel_size, output_dir, prefix, materials, 0)

    def print_progress(progress):
        print(f"Compilation progress: {progress*100:.2f}%")

    compiler.set_progress_callback(print_progress)
    compiler.compile()


