import pyvcad as pv
import pyvcad_rendering as viz

render = True
export = False
materials = pv.default_materials
red = materials.id("white")
blue = materials.id("blue")
liquid = materials.id("liquid")

box_dims = pv.Vec3(160, 40, 20)
unit_cell_size = pv.Vec3(10,10,10)
strut_diameter = 1.5
unit_cell_type = pv.LatticeType.BodyCenteredCubic

# Create a lattice and fill a rect prism with it
cell = pv.GraphLattice(unit_cell_type, unit_cell_size, strut_diameter)
lattice_fill = pv.Tile(cell)
bar = pv.RectPrism(pv.Vec3(0,0,0), box_dims)
filled_bar = pv.BBoxIntersection([lattice_fill, bar])


# Apply a grading to the lattice using the volume fractions attribute.
# UNCOMMENT ONE OF THE FOLLOWING MAPS to pick a grading.

volume_fraction_map = [
    ("x/150 + 0.5", red),
    ("-x/150 + 0.5", blue),
] # Linear crossfade between red and blue

# volume_fraction_map = [
#     ("min(max((-x/260)+0.75,0.5),1)", red),
#     ("min(max((x/260)+0.25,0),0.5)", blue),
# ] # Mechanical crossfade between red (soft) and blue (hard)

# volume_fraction_map = [
#     ("min(max(-x/160,0),0.5)", red), # Hard material
#     ("min(min(max((x+160)/160,0.5),1),min(max(1-x/400,0.8),1))", blue), # Soft material
#     ("min(max(x/400,0),0.2)", liquid), # Liquid material
# ] # Three-material crossfade between hard, soft and softer (with liquid)

filled_bar.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute(volume_fraction_map)
)
root = filled_bar

if render:
    viz.Render(root, materials)

if export:
    output_dir = "output/"
    prefix = "bar_"
    voxel_size = pv.Vec3(0.0423,0.0846,0.027)
    liquid_keepout = 0.6 # mm

    import pyvcad_compilers as pvc
    print(f"Output Directory: {output_dir}")

    # Delete the output directory if it already exists
    import shutil, os
    if export and os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    #Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    compiler = pvc.MaterialInkjetCompiler(root, voxel_size, output_dir, prefix, materials, liquid_keepout)

    def print_progress(progress):
        print(f"Compilation progress: {progress*100:.2f}%")

    compiler.set_progress_callback(print_progress)
    compiler.compile()