import pyvcad as pv
import pyvcad_rendering as viz

from resolution_matrix_scene import ATTRIBUTE_COLOR, STRATEGY_SUM, build_resolution_scene


materials = pv.default_materials

# Preview one representative cell from the conflict-resolution matrix.
root, materials = build_resolution_scene(ATTRIBUTE_COLOR, STRATEGY_SUM, materials)

viz.Render(root, materials)
