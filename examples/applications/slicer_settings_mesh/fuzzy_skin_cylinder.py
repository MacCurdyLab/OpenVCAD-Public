import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_compilers as pvc

# Parametric upright cylinder (Z is the long axis). Defaults: 100 mm tall, 15 mm radius.
cylinder_height_mm = 100.0
cylinder_radius_mm = 15.0

# Fuzzy skin thickness ramp (mm). The expression is normalized by the cylinder height.
fuzzy_skin_thickness_bottom_mm = 0.0
fuzzy_skin_thickness_top_mm = 0.75

half_h = 0.5 * cylinder_height_mm
z_normalized_expr = f"clamp((z + {half_h}) / ({cylinder_height_mm}), 0, 1)"
fuzzy_expr = (
    f"{fuzzy_skin_thickness_bottom_mm} + "
    f"({fuzzy_skin_thickness_top_mm} - {fuzzy_skin_thickness_bottom_mm}) * {z_normalized_expr}"
)

cylinder = pv.Cylinder(pv.Vec3(0, 0, 0), cylinder_radius_mm, cylinder_height_mm)
cylinder.set_attribute(
    pv.DefaultAttributes.FUZZY_SKIN_THICKNESS,
    pv.FloatAttribute(fuzzy_expr),
)

root = cylinder
viz.Render(root)

def report_progress(progress):
    print(f"Slicer export progress: {progress * 100:.1f}%")

regions = 3
compiler = pvc.PrusaSlicerProjectCompiler(
    root,
    pv.Vec3(0.15, 0.15, 0.15),
    f'output/fuzzy_skin_cylinder_{regions}.3mf',
    regions,
)
compiler.set_progress_callback(report_progress)
compiler.compile()
