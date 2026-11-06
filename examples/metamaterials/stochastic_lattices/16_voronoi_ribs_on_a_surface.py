import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

# Seeds spread over a surface, and the Voronoi cells they own on it. The cell boundaries become
# ribs. The spacing is a field, so the cells grow from about 3 mm on the left to 6 mm on the right.
body = pv.Torus(18.0, 8.0)
mesh = pv.SurfaceMesh(body, 0.4)
spacing = pv.FloatAttribute("4.5 + x / 17")
seeds = mm.surface_seeds(mesh, spacing, seed=2)

# Left: round ribs along the cell boundaries, centred on the surface.
ribs = mm.surface_voronoi_ribs(mesh, seeds, beam_thickness=1.0)

# Right: walls across the surface along the same boundaries, 3 mm tall (half in, half out),
# thicker at the top.
walls = mm.surface_voronoi_plates(body, seeds, rib_height=3.0,
                                  wall_thickness=pv.FloatAttribute("0.6 + 0.04 * (z + 8)"))

root = pv.Union(pv.Translate(-30.0, 0.0, 0.0, ribs), pv.Translate(30.0, 0.0, 0.0, walls))

viz.Render(root)
