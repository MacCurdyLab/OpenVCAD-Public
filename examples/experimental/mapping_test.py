import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials



map = pv.Map("surface_a_part.off", "surface_a_part.off")

bunny = pv.Mesh("surface_a_whole.stl", materials.id("gray"), True)

root = pv.Union(False, [map, bunny])

viz.Render(root, materials)
