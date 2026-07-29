import pyvcad as pv
import pyvcad_rendering as viz

# The height is measured from the bottom to top of the text (all lines)
text_height = 50

# The depth is the 3D height of the text
text_depth = 5

font = "Consolas"
font_aspect = pv.FontAspect.Italic
horizontal_alignment = pv.HorizontalAlignment.Center # Left, Center, Right
vertical_alignment = pv.VerticalAlignment.Center # Bottom, Center, Top

# You can create multiple lines using '\n'
text = pv.Text("Welcome to OpenVCAD\nMAC Lab", text_height, text_depth, font_aspect, font, horizontal_alignment, vertical_alignment)
root = text

viz.Render(root) # NOTE: Switch to at least "Menu->View->Quality->Medium" to view