import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_compilers as pvc
import pyvcad_attribute_resolver as resolver

resolver.register_foaming_conversions()

# temperature_attr = pv.FloatAttribute("x/2.79 + 238")
temperature_attr = pv.FloatAttribute("max(min((x/3+236),256),216)")

rect_prism = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(200,10,10))
rect_prism.set_attribute(pv.DefaultAttributes.TEMPERATURE, temperature_attr)

root = resolver.adapt(rect_prism, ["flow_rate"], tags=["foaming_pla"])

viz.Render(root)

printer_profile_path = "../profiles/prusa_xl_multitool.ini"
filament_profile_path = "../profiles/ColorFabb_LW_PLA.ini"
regions = 10

compiler = pvc.PrusaSlicerProjectCompiler(root, pv.Vec3(0.25,0.25,0.25),
                                     "compensation_pla_demo.3mf",
                                     regions,
                                     printer_profile_path, filament_profile_path)
compiler.compile()
