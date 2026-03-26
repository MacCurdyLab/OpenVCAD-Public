import pyvcad as pv
import pyvcad_rendering as viz

def make_checkerboard(
    center: pv.Vec3,
    total_size_xy: pv.Vec3,   # only x,y used; z ignored here
    tiles_x: int,
    tiles_y: int,
    tile_height: float,
    white_name: str = "white",
    black_name: str = "black",
    start_white_at_lower_left: bool = True
) -> pv.Union:
    """
    Build a single-layer checkerboard of RectPrism tiles.
    - center: board center in 3D (z is the board mid-plane)
    - total_size_xy: overall X/Y size (use pv.Vec3(w, h, 0) or pv.Vec3(w,h,any))
    - tiles_x / tiles_y: number of tiles along X and Y
    - tile_height: thickness in Z for each cube/tile
    """

    materials = pv.default_materials
    mat_white = materials.id(white_name)
    mat_black = materials.id(black_name)

    union = pv.Union()

    board_w = float(total_size_xy.x)
    board_h = float(total_size_xy.y)
    tile_w  = board_w / tiles_x
    tile_h  = board_h / tiles_y

    # min corner of the board (lower-left in XY) at z centered
    min_x = center.x - board_w * 0.5
    min_y = center.y - board_h * 0.5
    cz    = center.z  # mid-plane

    # Decide the color parity of the (0,0) tile (lower-left)
    base_white = 0 if start_white_at_lower_left else 1

    for ix in range(tiles_x):
        for iy in range(tiles_y):
            # tile center
            cx = min_x + (ix + 0.5) * tile_w
            cy = min_y + (iy + 0.5) * tile_h

            # alternating material
            parity = (ix + iy + base_white) % 2
            mat = mat_white if parity == 0 else mat_black

            # build cube (rectangular prism) for this tile
            size = pv.Vec3(tile_w, tile_h, tile_height)
            center_pt = pv.Vec3(cx, cy, cz)
            tile = pv.RectPrism(center_pt, size, mat)
            union.add_child(tile)

    return union


# -------------------------
# Example usage
# -------------------------
materials = pv.default_materials
white = materials.id("white")
black = materials.id("black")
green = materials.id("green")

checker = make_checkerboard(
    center=pv.Vec3(0, 0, 0),
    total_size_xy=pv.Vec3(225, 225, 0),
    tiles_x=10,
    tiles_y=10,
    tile_height=5.0,
    white_name="white",
    black_name="black",
    start_white_at_lower_left=True
)


size = pv.Vec3(225,225,20)
unit_cell_size = pv.Vec3(7,7,7)
strut_diameter = 0.55
cell_bcc = pv.GraphLattice(pv.LatticeType.BodyCenteredCubic, unit_cell_size, strut_diameter, 1)
lattice_fill = pv.Tile(cell_bcc) 
rect_prism = pv.RectPrism(pv.Vec3(0,0,0), size)
filled_rect_prism = pv.Intersection(False, [lattice_fill, rect_prism])

object_to_wrap = checker

base_surface = pv.Sphere(pv.Vec3(0, 0, 0), 100.0, green)
conformal = pv.ConformalMap()
conformal.set_left(base_surface)
conformal.set_right(object_to_wrap)

union = pv.Union()
union.add_child(conformal)
union.add_child(base_surface)

root = union

viz.Render(root, materials)
