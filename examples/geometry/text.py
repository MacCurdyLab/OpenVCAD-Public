"""
Text Demo - Extruded 3D text from a system font.

Text lays the string out in the XY plane and extrudes it along Z. height is
the font size of one line (each extra line adds a line of spacing below it)
and depth is the extrusion thickness. When the requested font is not
installed, a fallback system font is used and a warning is printed.
"""
import pyvcad as pv
import pyvcad_rendering as viz

text_height = 50.0  # mm, font size of one line
text_depth = 5.0    # mm

# '\n' starts a new line.
text = pv.Text("Welcome to OpenVCAD\nMAC Lab", text_height, text_depth,
               aspect=pv.FontAspect.Italic,
               font="Consolas",
               h_align=pv.HorizontalAlignment.Center,  # Left, Center, Right
               v_align=pv.VerticalAlignment.Center)    # Bottom, Center, Top

root = text

viz.Render(root)  # NOTE: Switch to at least "Render -> Quality -> Medium" to view
