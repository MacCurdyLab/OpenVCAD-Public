import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

# Two copies of the same 2 x 2 x 2 BCC strut lattice side by side.
left_map = mm.rectangular_cell_map((pv.Vec3(-25, -10, -10), pv.Vec3(-5, 10, 10)), cells=(2, 2, 2))
right_map = mm.rectangular_cell_map((pv.Vec3(5, -10, -10), pv.Vec3(25, 10, 10)), cells=(2, 2, 2))

# Left: sharp nodes. Right: member_blend_radius fillets every node where struts meet. Struts that
# neighbouring cells share count once, so only the nodes thicken.
sharp = mm.bcc(left_map, beam_radius=0.8)
filleted = mm.bcc(right_map, beam_radius=0.8, member_blend_radius=0.25)

root = pv.Union(sharp, filleted)
viz.Render(root)
