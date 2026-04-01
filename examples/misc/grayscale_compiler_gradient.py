import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz


# Load the default material definitions shipped with pyvcad.
materials = pv.default_materials

# The grayscale compiler requires exactly two materials in the design.
# low_material is mapped to grayscale 0 (black) and high_material is
# mapped to grayscale 255 (white).
low_material = materials.id("black")
high_material = materials.id("white")

# Create a simple rectangular bar. The center z position of 5 mm with a
# 10 mm height places the object on the z=0 build plane and gives a
# 10-layer export when voxel_size.z is 1 mm.
bar = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 5.0),
    pv.Vec3(40.0, 20.0, 10.0),
    low_material
)

# Apply a two-material functional grade along X.
# At x = -20 mm the object is 100% red.
# At x =   0 mm the object is a 50/50 mix.
# At x =  20 mm the object is 100% blue.
root = pv.FGrade(
    ["0.5 - x / 40.0", "0.5 + x / 40.0"],
    [low_material, high_material],
    True,
    bar
)

# Configure the grayscale compiler.
# voxel_size controls the sampling pitch of the volumetric export.
# This is in mm
voxel_size = pv.Vec3(1.0, 1.0, 1.0)

# printer_volume defines the custom build volume used for the exported
# bitmap stack. This example uses a larger XY volume than the object so the
# centering behavior is easy to inspect. This is in mm
printer_volume = pv.Vec3(60.0, 40.0, 20.0)

# Computed image resolution is printer_volume / voxel_size.
printer_resolution_x = int(printer_volume.x / voxel_size.x)
printer_resolution_y = int(printer_volume.y / voxel_size.y)
printer_resolution_z = int(printer_volume.z / voxel_size.z)
print(f"Computed printer resolution: {printer_resolution_x} x {printer_resolution_y} x {printer_resolution_z}")


output_directory = "output_stack"
file_prefix = "slice_"

# Render the graded object first so it can be inspected visually. This is a
# blocking call. Close the render window to continue to the export step.
viz.Render(root, materials)

compiler = pvc.GrayscaleCompiler(
    root,
    voxel_size,
    printer_volume,
    low_material,
    high_material,
    output_directory,
    file_prefix
)

compiler.compile()
print("Export complete!")
