import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_compilers as pvc
import pyvcad_attribute_resolver as resolver

resolver.register_foaming_conversions()

temperature_attr = pv.FloatAttribute("x/2.79 + 222")

rect_prism = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(100,10,2))
rect_prism.set_attribute(pv.DefaultAttributes.TEMPERATURE, temperature_attr)

root = resolver.adapt(rect_prism, ["flow_rate"], tags=["foaming_tpu"])

viz.Render(root)

printer_profile_path = "../profiles/prusa_mk4s_profile.ini"
filament_profile_path = "../profiles/ColorFabb_VarioShore_TPU.ini"
regions = 10

compiler = pvc.PrusaSlicerProjectCompiler(root, pv.Vec3(0.25,0.25,0.25),
                                     "output.3mf",
                                     regions,
                                     printer_profile_path, filament_profile_path)
compiler.compile()
