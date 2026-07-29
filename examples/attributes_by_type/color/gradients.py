import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

voxel_size = pv.Vec3(0.0423,0.0846,0.027)
output_dir = "new_gradients/"
prefix = "swatch_"

swatch_size = pv.Vec3(2.5,10,2.5)
num_steps = 100

# raw_palettes={
#     "viridis":[(68,1,84),(59,82,139),(33,145,140),(94,201,98),(253,231,37)],
#     "magma":[(0,0,4),(84,17,68),(187,55,84),(249,142,8),(251,252,191)],
#     "inferno":[(0,0,4),(87,15,109),(187,55,84),(249,142,8),(252,255,164)],
#     "plasma":[(13,8,135),(126,3,168),(203,71,119),(248,149,64),(240,249,33)],
#     "cividis":[(0,34,77),(67,85,130),(128,129,145),(190,172,129),(255,233,69)],
#     "jet":[(0,0,131),(0,60,170),(5,255,255),(255,255,0),(128,0,0)],
#     "gray":[(0,0,0),(255,255,255)],
#     "bone":[(0,0,0),(84,84,116),(168,200,200),(255,255,255)],
#     "midjet": [(0,60,170),(5,255,255),(255,255,0)]
# }

raw_palettes={
    "gray":[(0,0,0),(255,255,255)],
    "midjet": [(0,60,170),(5,255,255),(255,255,0)],
    "midviridis":[(68,1,84),(59,82,139),(33,145,140),(94,201,98)],
    "midcividis":[(0,34,77),(67,85,130),(128,129,145),(190,172,129)],
    "midmagma":[(0,0,4),(84,17,68),(187,55,84),(249,142,8)],
}

def lerp(a,b,t): return a+(b-a)*t
def interp_color(palette,t):
    n=len(palette)-1; x=t*n; i=int(x); f=x-i
    if i>=n: return tuple(v/255 for v in palette[-1])
    c1,c2=palette[i],palette[i+1]
    return tuple((lerp(c1[j],c2[j],f))/255 for j in range(3))

def make_swatch(x_index,y_index, color):
    swatch = pv.RectPrism(pv.Vec3(x_index*swatch_size.x, y_index*swatch_size.y, 0), swatch_size)
    swatch.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(color[0], color[1], color[2], color[3]))
    return swatch

root = pv.BBoxUnion()

# For each raw palette, create a row of swatches with a gradient with the number of steps
for p_index, (p_name, p_colors) in enumerate(raw_palettes.items()):
    for step in range(num_steps):
        t = step / (num_steps - 1)
        color_rgb = interp_color(p_colors, t)
        color_rgba = (color_rgb[0], color_rgb[1], color_rgb[2], 1.0)

        swatch = make_swatch(step, p_index, color_rgba)
        root.add_child(swatch)

viz.Render(root)

compiler = pvc.ColorInkjetCompiler(root, voxel_size, output_dir, prefix)

def print_progress(progress):
    print(f"Compilation progress: {progress*100:.2f}%")

compiler.set_progress_callback(print_progress)
compiler.compile()
