import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_compilers as pvc
import pyvcad_attribute_resolver as resolver

resolver.register_foaming_conversions()

# Settings
printer_profile_path = "../profiles/prusa_mk4s_profile.ini"
filament_profile_path = "../profiles/ColorFabb_VarioShore_TPU.ini"
regions = 10
gradient_mode = "shore_hardness" # "temperature" or "shore_hardness"

# Object
temperature_attr = pv.FloatAttribute("max(y/1.94 + 204, 204)")
shore_hardness_attr = pv.FloatAttribute("max(min(-y/2.25 + 90,90), 60)")

mesh_path = "hainsworth_actuator.stl"
mesh = pv.Mesh(mesh_path)
if gradient_mode == "temperature":
    mesh.set_attribute(pv.DefaultAttributes.TEMPERATURE, temperature_attr)
elif gradient_mode == "shore_hardness":
    mesh.set_attribute(pv.DefaultAttributes.SHORE_HARDNESS, shore_hardness_attr)
else:
    raise ValueError("Invalid gradient mode. Must be 'temperature' or 'shore_hardness'.")

# Resolve the full conversion chain: shore_hardness -> temperature -> flow_rate
# or just temperature -> flow_rate, depending on gradient_mode
root = resolver.adapt(mesh,
                      ["temperature", "flow_rate"],
                      tags=["foaming_tpu"])

viz.Render(root)

compiler = pvc.PrusaSlicerProjectCompiler(root, pv.Vec3(0.25,0.25,0.25),
                                     "output.3mf",
                                     regions,
                                     printer_profile_path, filament_profile_path)
compiler.compile()
