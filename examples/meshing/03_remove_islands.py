"""Find and remove floating fragments, here left where a graded wall gets too thin to mesh."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

VOXEL_SIZE = 0.3  # mm
THICK_WALL = 1.2  # mm, wall thickness at the left end
THIN_WALL = 0.15  # mm, wall thickness at the right end (thinner than the voxel size)
MIN_VOLUME = 1.0  # mm^3; bodies smaller than this are treated as islands

# A gyroid block whose wall thickness is graded along x. Where the wall drops below about one voxel,
# the mesh breaks into small disconnected pieces that would float free in a print.
cell_map = mm.rectangular_cell_map((pv.Vec3(-20, -10, -10), pv.Vec3(20, 10, 10)), cells=(4, 2, 2))
wall = cell_map.u_field.map_range(0.0, 4.0, THICK_WALL, THIN_WALL)
root = mm.gyroid(cell_map, wall_thickness=wall)
mesh = pv.SurfaceMesh(root, VOXEL_SIZE)

pieces = mesh.connected_components()
small = [piece for piece in pieces if piece.volume < MIN_VOLUME]
print(f"{len(pieces)} connected pieces; {len(small)} below {MIN_VOLUME} mm^3 "
      f"(largest of those {max((p.volume for p in small), default=0.0):.3f} mm^3)")

# Remove every body below MIN_VOLUME. keep_largest=True would keep only the main body instead.
clean = mesh.remove_small_components(min_volume=MIN_VOLUME)
print(f"after cleanup: {len(clean.connected_components())} piece(s), "
      f"{mesh.triangle_count - clean.triangle_count:,} triangles removed")

viz.Render(pv.Mesh(clean))
