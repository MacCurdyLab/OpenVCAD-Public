# Script to create a lattice/ TPMS filled bar with functionally graded properties. We hand these out of conferences as freebies!
# At one end the lattice is hard, at the other end it is soft. We mix soft (Agilus30), hard (Vero) and non-curing cleanser material (to make it very soft).
# The gradient expressions can be visualized here: https://www.desmos.com/calculator/5ybcj1n0gk
# The geometry for the bar can either be a tiled strut lattice or a TPMS mesh.
# We also added some text to the model.
import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.j750_materials
red = materials.id("VeroYellow") # Vero
blue = materials.id("Agilus30Mgn") # Ag
green = materials.id("Agilus30Blk") # Ag Contrast
liquid = materials.id("M.Cleanser") # Cleanser

box_dims = pv.Vec3(60, 20, 10)

use_strut_lattice = True
unit_cell_size = pv.Vec3(5,5,5)
strut_diameter = 0.75
unit_cell_type = pv.LatticeType.BodyCenteredCubic
unit_cell_title_text = "Unit Cell:"
unit_cell_text = "BCC"
project_path = '../data/3d_models/unit_cells/'
mesh_path = project_path + "diamond_tpms.3mf"

if use_strut_lattice:
    # Create a lattice and fille a rect prism with it
    cell = pv.GraphLattice(unit_cell_type, unit_cell_size, strut_diameter, red)
    lattice_fill = pv.Tile(cell)
    bar = pv.RectPrism(pv.Vec3(0,0,0), box_dims, red)
    filled_bar = pv.Intersection(False, [lattice_fill, bar])
else:
    filled_bar = pv.Mesh(mesh_path, red)

text_bar = pv.RectPrism(pv.Vec3(-box_dims.x/2 - 2,0,0), pv.Vec3(5, box_dims.y, box_dims.z))
union = pv.Union(False, [filled_bar, text_bar])

a = box_dims.x
h_left = 0.55   # hard at x = -a/2
s_left = 1.0 - h_left   # soft at x = -a/2
x0     = 15   # where hard=0, soft=1, liquid starts rising
l_max  = 0.20   # liquid at x = +a/2   (soft there = 1 - l_max)

# 0–1 ramps as inline expressions (strings) using min/max clamps
tL = f"min(max((x + {a}/2)/(({x0}) + {a}/2), 0), 1)"      # ramps from 0 at x=-a/2 to 1 at x=x0
tR = f"min(max((x - ({x0}))/({a}/2 - ({x0})), 0), 1)"   # ramps from 0 at x=x0 to 1 at x=+a/2

# Piecewise-linear fractions built from the ramps
hard_expr   = f"min(max(({h_left})*(1 - {tL}), 0), 1)"
soft_expr   = f"min(max(({s_left}) + (1 - ({s_left}))*{tL} - ({l_max})*{tR}, 0), 1)"
liquid_expr = f"min(max(({l_max})*{tR}, 0), 1)"

fgrade = pv.FGrade(
    [hard_expr, soft_expr, liquid_expr],
    [red, blue, liquid],
    False
)
fgrade.set_child(union)

# Text
text_height = 3.65
text_depth = 1
font = "Arial"
font_aspect = pv.FontAspect.Bold
horizontal_alignment = pv.HorizontalAlignment.Center # Left, Center, Right
vertical_alignment = pv.VerticalAlignment.Center # Bottom, Center, Top
vcad_text_text = pv.Text("OpenVCAD", text_height, text_depth, green, font_aspect, font, horizontal_alignment, vertical_alignment)
vcad_text_rotate = pv.Rotate(0,0,-90, pv.Vec3(0,0,0), vcad_text_text)
vcad_text_translate = pv.Translate(-box_dims.x/2 - 2, 0, box_dims.z/4+2.0135, vcad_text_rotate)

maclab_text = pv.Text("MatterAssembly.org/\nOpenVCAD", 1.9, text_depth, green, font_aspect, font, horizontal_alignment, vertical_alignment)
maclab_text_rotate = pv.Rotate(180,0,-90, pv.Vec3(0,0,0), maclab_text)
maclab_text_translate = pv.Translate(-box_dims.x/2 - 2, 0, -box_dims.z/4-2.0135, maclab_text_rotate)

unit_cell_text = pv.Text(f"{unit_cell_title_text}:\n{unit_cell_text}", 3.65, 1, green, font_aspect, font, horizontal_alignment, vertical_alignment)
unit_cell_text_rotate = pv.Rotate(90,90,0, pv.Vec3(0,0,0), unit_cell_text)
unit_cell_text_translate = pv.Translate(-box_dims.x/2 - 4, 0, 0, unit_cell_text_rotate)

# Composite Object
union_b = pv.Union(False, [unit_cell_text_translate, maclab_text_translate, vcad_text_translate, fgrade])
root = union_b

viz.Render(root, materials)