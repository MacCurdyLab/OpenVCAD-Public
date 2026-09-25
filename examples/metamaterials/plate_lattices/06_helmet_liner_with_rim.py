import time
import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz
import os
import sys

# IO
CURR_PATH = os.path.dirname(os.path.abspath(__file__))
HEADFORM_PATH = os.path.join(CURR_PATH, "headform.stl")
OUTPUT_STL = "HELMET_LINER.stl"

# LATTICE CONFIG
U_CELLS, V_CELLS, NORMAL_CELLS = 15, 15, 4
METHOD = "lscm" # "lscm", "arap", or "authalic"
STANDOFF = 4.0 # stand-off distance from the head form, mm
LINER_THICKNESS = 25.0 # liner thickness along the surface normal, mm
WALL_THICKNESS_MIN = 0.5 # outermost layer, mm
WALL_THICKNESS_MAX = 1.0 # layer against the scalp, mm
ECCENTRICITY_MIN = 0.5 # outermost layer
ECCENTRICITY_MAX = 1.0 # layer against the scalp
USE_TRIANGULATED = False # does bilinear if False
RIM_WIDTH = 1.0 # inward band width, mm. Set to None to skip the rim.
VOXEL_SIZE = 0.4 # mm

materials = pv.default_materials
white = materials.id("white")

start_time = time.time()
headform_mesh = pv.SurfaceMesh(HEADFORM_PATH, disable_validation=True)
surface = pv.TriangleMeshSurface(headform_mesh.vertices, headform_mesh.triangles, method=METHOD)
cell_map = mm.cell_map_from_surface(
    surface,
    cells=(U_CELLS, V_CELLS, NORMAL_CELLS),
    height=LINER_THICKNESS,
    linear=False,
    standoff=STANDOFF,
)
if not cell_map.validate().valid:
    raise RuntimeError("Cell map is folded, reduce STANDOFF or LINER_THICKNESS")

# GRADED FIELDS
w = cell_map.w_field
wall = w.map_range(0.5, NORMAL_CELLS - 0.5, WALL_THICKNESS_MAX, WALL_THICKNESS_MIN)
pre_buckle = w.map_range(0.5, NORMAL_CELLS - 0.5, ECCENTRICITY_MAX, ECCENTRICITY_MIN)

lattice = mm.plate_lattice(
    cell_map,
    wall_thickness=wall,
    eccentricity=pre_buckle,
    surface_mode="triangulated" if USE_TRIANGULATED else "bilinear",
    surface_tolerance=0.04,
)

if RIM_WIDTH:
    root = pv.Union(lattice, mm.rim(cell_map, width=RIM_WIDTH))
else:
    root = lattice

# MATERIAL
root.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute([(1.0, white)]),
)

mesh = pv.SurfaceMesh(root, VOXEL_SIZE)
mesh.write_stl(OUTPUT_STL)
print(f"Built and exported stl in {time.time() - start_time:.2f} seconds")
