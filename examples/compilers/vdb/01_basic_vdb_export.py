"""
VDB compiler - basic export
===========================

Builds a rectangular design with scalar, Vec3, Vec4, and volume-fraction
attributes. The VDB compiler writes the SDF, optional occupancy, and supported
attribute grids while intentionally skipping volume fractions.
"""
import os

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.default_materials

bar_length = 30.0
bar_width = 12.0
bar_height = 10.0
half_length = 0.5 * bar_length

bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_length, bar_width, bar_height))
ramp = f"clamp((x + {half_length}) / {bar_length}, 0, 1)"

bar.set_attribute(
    pv.DefaultAttributes.TEMPERATURE,
    pv.FloatAttribute(f"190 + 35 * {ramp}"),
)
bar.set_attribute(
    pv.DefaultAttributes.COLOR_RGB,
    pv.Vec3Attribute(ramp, "0.25", f"1 - {ramp}"),
)
bar.set_attribute(
    pv.DefaultAttributes.COLOR_RGBA,
    pv.Vec4Attribute(ramp, f"1 - {ramp}", "0.35", "1.0"),
)
bar.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute([
        (f"1 - {ramp}", 1),
        (ramp, 2),
    ]),
)

root = bar

output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "basic_vdb_export.vdb")
if os.path.exists(output_path):
    os.remove(output_path)

compiler = pvc.VdbCompiler(
    root,
    pv.Vec3(0.5, 0.5, 0.5),
    output_path,
    attributes_to_export=[],
    include_occupancy=True,
)
compiler.compile()

print("Wrote", output_path)
print("Expected grids: surface, occupancy, temperature, color_rgb, color_rgba")
print("Skipped grid: volume_fractions")

viz.Render(root, materials)
