"""
Slicer project - temperature + flow (virtual extrusion)
=======================================================

**TEMPERATURE** field with **FLOW_RATE** from a lookup (**AttributeModifier**),
similar to the foaming PLA compensation demo. Requires printer and filament
**.ini** profiles for virtual-extrusion G-code injection.

Companion to: docs/source/guides/compilers/slicer-project.md
See also: examples/applications/foaming_filaments/compensation_demo/compensation_pla_demo.py
"""
import os
import sys

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

_here = os.path.dirname(os.path.abspath(__file__))
_profiles = os.path.normpath(os.path.join(_here, "..", "..", "applications", "foaming_filaments", "profiles"))
sys.path.insert(0, _profiles)
from flow_compensation_data import foaming_pla_flow_compensation

temperature_attr = pv.FloatAttribute("max(min((x/3+236),256),216)")

rect_prism = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(200, 10, 10))
rect_prism.set_attribute(pv.DefaultAttributes.TEMPERATURE, temperature_attr)

flow_entries = [pv.LookupTableEntry(kv[0], kv[0], kv[1]) for kv in foaming_pla_flow_compensation]
mod_func = pv.LookupTableConverter(
    [pv.DefaultAttributes.TEMPERATURE],
    [pv.DefaultAttributes.FLOW_RATE],
    flow_entries,
    pv.InterpolationMode.LINEAR,
)
mod = pv.AttributeModifier(mod_func, rect_prism)

root = mod
viz.Render(root)

out_dir = os.path.join(_here, "output")
os.makedirs(out_dir, exist_ok=True)
out_3mf = os.path.join(out_dir, "temperature_compensation_demo.3mf")

printer_profile_path = os.path.join(_profiles, "prusa_xl_multitool.ini")
filament_profile_path = os.path.join(_profiles, "ColorFabb_LW_PLA.ini")
regions = 10

compiler = pvc.PrusaSlicerProjectCompiler(
    root,
    pv.Vec3(0.25, 0.25, 0.25),
    out_3mf,
    regions,
    printer_profile_path,
    filament_profile_path,
)
compiler.compile()
print("Wrote", out_3mf)
