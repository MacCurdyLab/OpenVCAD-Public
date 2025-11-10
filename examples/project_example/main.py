# pyvcad is the main library and pyvcad_rendering is the visualization library
import pyvcad as pv
import pyvcad_compilers as pvc # If you need direct access to compilers, otherwise use pyvcad_rendering.Export()
import pyvcad_rendering as viz

# Load some material definitions
materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

# Create a simple rectangular prism as our geometry
# Don't care about material here, we will replace it with a gradient
bar = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(100,50,10), red)

# A functional gradient that is 100% blue at x=-50 and 100% at x=50
graded_bar = pv.FGrade(["x/100 + 0.5", "-x/100 + 0.5"],
                       [red, blue], False)
graded_bar.set_child(bar) # Nest the bar inside the gradient to apply the gradient to it

# Render the object, note that this is a blocking call and
# will not continue until the window is closed
viz.Render(graded_bar, materials)

# Export the object for 3D printing, simulation, etc.
# This brings up a wizard to guide you through the export process
viz.Export(graded_bar, materials)