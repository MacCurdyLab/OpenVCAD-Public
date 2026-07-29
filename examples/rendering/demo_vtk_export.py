import pyvcad as pv
from pyvcad_rendering.vtk_export import export_iso_surface_vtk, export_volume_vtk
from pyvcad_rendering import Render_Image

# Build your object
sphere = pv.Sphere(pv.Vec3(0, 0, 0), 10)
cube = pv.Sphere(pv.Vec3(5, 5, 5), 5)

# Creating an object with multiple attributes
cube.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(1.0, 0.0, 0.0, 1.0))
cube.set_attribute("temperature", pv.FloatAttribute(100.0))

sphere.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(0.0, 1.0, 0.0, 1.0))
sphere.set_attribute("temperature", pv.FloatAttribute(50.0))

union = pv.Union(cube, sphere)

# Export isosurface
print("Exporting Isosurface VTK...")
export_iso_surface_vtk(
    union, 
    "test_isosurface.vtp", 
    quality="medium", 
    progress_callback=lambda p: print(f"  Iso-surface progress: {p:.1f}%")
)
print("Isosurface exported to test_isosurface.vtp")

# Export volume
print("\nExporting Volume VTK...")
export_volume_vtk(
    union, 
    "test_volume.vti", 
    quality="medium", 
    progress_callback=lambda p: print(f"  Volume progress: {p:.1f}%")
)
print("Volume exported to test_volume.vti")
