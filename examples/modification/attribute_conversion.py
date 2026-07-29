"""
This example demonstrates standalone attribute conversion in OpenVCAD.
It shows how to transform attributes using various patterns:
(a) Single-to-Single: 'shore-hardness' -> Color (COLOR_RGBA) using a LookupTableConverter
(b) Single-to-Single: 'shore-hardness' -> Temperature using an ExpressionConverter
(c) Multi-to-Single: 'shore-hardness' + 'density' -> Modulus using an ExpressionConverter
(d) Single-to-Multi: 'temperature' -> Elongation + Flow Rate using an ExpressionConverter
"""
import pyvcad as pv
import pyvcad_rendering as viz

# 1. Create a simple bar geometry
# We'll make a bar that is 100mm long, centered at 0,0,0
bar_length = 100.0
bar_width = 20.0
bar_thickness = 5.0
bar = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(bar_length, bar_width, bar_thickness))

# 2. Add initial attributes to the bar
# Shore Hardness: 0 to 100 gradient along X
shore_expr = f"((x + {bar_length/2}) / {bar_length}) * 100"
bar.set_attribute(pv.DefaultAttributes.SHORE_HARDNESS, pv.FloatAttribute(shore_expr))

# Density: constant value
bar.set_attribute(pv.DefaultAttributes.DENSITY, pv.FloatAttribute(1.2))

# -----------------------------------------------------------------------------
# Method (A): Single-to-Single (Lookup Table)
# SHORE_HARDNESS -> COLOR_RGBA
# -----------------------------------------------------------------------------
color_entries = [
    pv.LookupTableEntry(0.0, 33.3, pv.Vec4(0, 0, 1, 1.0)),  # Blue
    pv.LookupTableEntry(33.3, 66.6, pv.Vec4(0, 1, 0, 1.0)), # Green
    pv.LookupTableEntry(66.6, 100.0, pv.Vec4(1, 0, 0, 1.0)) # Red
]

color_converter = pv.LookupTableConverter(
    input_attributes=[pv.DefaultAttributes.SHORE_HARDNESS],
    output_attributes=[pv.DefaultAttributes.COLOR_RGBA],
    entries=color_entries,
    mode=pv.InterpolationMode.STEP
)
bar = pv.AttributeModifier(color_converter, bar)

# -----------------------------------------------------------------------------
# Method (B): Single-to-Single (Expression)
# SHORE_HARDNESS -> TEMPERATURE
# -----------------------------------------------------------------------------
temp_converter = pv.ExpressionConverter(
    input_attributes=[pv.DefaultAttributes.SHORE_HARDNESS],
    output_attributes=[pv.DefaultAttributes.TEMPERATURE],
    expressions=[f"{pv.DefaultAttributes.SHORE_HARDNESS} * 0.5 + 20.0"]
)
bar = pv.AttributeModifier(temp_converter, bar)

# -----------------------------------------------------------------------------
# Method (C): Multi-to-Single (Expression)
# SHORE_HARDNESS + DENSITY -> MODULUS
# -----------------------------------------------------------------------------
# Here we use two input attributes to calculate a new one
modulus_converter = pv.ExpressionConverter(
    input_attributes=[pv.DefaultAttributes.SHORE_HARDNESS, pv.DefaultAttributes.DENSITY],
    output_attributes=[pv.DefaultAttributes.MODULUS],
    expressions=[f"{pv.DefaultAttributes.SHORE_HARDNESS} * {pv.DefaultAttributes.DENSITY} * 10.0"]
)
bar = pv.AttributeModifier(modulus_converter, bar)

# -----------------------------------------------------------------------------
# Method (D): Single-to-Multi (Expression)
# TEMPERATURE -> ELONGATION + FLOW_RATE
# -----------------------------------------------------------------------------
# Here we take one attribute and produce two distinct output attributes
ximo_converter = pv.ExpressionConverter(
    input_attributes=[pv.DefaultAttributes.TEMPERATURE],
    output_attributes=[pv.DefaultAttributes.ELONGATION, pv.DefaultAttributes.FLOW_RATE],
    expressions=[
        f"{pv.DefaultAttributes.TEMPERATURE} / 100.0", # Elongation
        f"{pv.DefaultAttributes.TEMPERATURE} * 2.0"    # Flow Rate
    ]
)
bar = pv.AttributeModifier(ximo_converter, bar)

# 3. Render the result
viz.Render(bar)
