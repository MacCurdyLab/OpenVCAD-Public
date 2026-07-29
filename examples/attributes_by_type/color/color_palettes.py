import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

voxel_size = pv.Vec3(0.0423,0.0846,0.027)
output_dir = "color_test_hybrid_yellow/"
prefix = "swatch_"

swatch_size = pv.Vec3(5,5,2.5)

alpha_values = [1.0, 0.8, 0.6, 0.4, 0.2, 0.1, 0.05, 0.025, 0.01]

colors = [
    (1.0, 0.0, 0.0), # Red
    (0.0, 1.0, 0.0), # Green
    (0.0, 0.0, 1.0), # Blue
    (0.0, 1.0, 1.0), # Cyan
    (1.0, 0.0, 1.0), # Magenta
    (1.0, 1.0, 0.0), # Yellow
    (1.0, 1.0, 1.0), # White
    (0.0, 0.0, 0.0), # Black
    (0.5, 0.5, 0.5), # Gray
    (1.0, 0.5, 0.0), # Orange
    (0.5, 0.0, 0.5), # Purple
    (0.6, 0.4, 0.2), # Brown
    (1.0, 0.41, 0.70) # Pink
]

def make_swatch(x_index,y_index, color):
    swatch = pv.RectPrism(pv.Vec3(x_index*swatch_size.x, y_index*swatch_size.y, 0), swatch_size)
    swatch.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(color[0], color[1], color[2], color[3]))
    return swatch

root = pv.BBoxUnion()

for y_index, alpha in enumerate(alpha_values):
    for x_index, color in enumerate(colors):
        swatch_color = (color[0], color[1], color[2], alpha)
        swatch = make_swatch(x_index, y_index, swatch_color)
        root.add_child(swatch)


viz.Render(root)

compiler = pvc.ColorInkjetCompiler(root, voxel_size, output_dir, prefix)

def print_progress(progress):
    print(f"Compilation progress: {progress*100:.2f}%")

compiler.set_progress_callback(print_progress)
compiler.compile()
