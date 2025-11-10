# Example from the paper "Implicit Modeling for 3D-printed Multi-material Computational Object Design via Python"
# Read full paper here: https://matterassembly.org/publications#wade2025pyvcad
import pyvcad as pv
import pyvcad_rendering as viz

def create_color_calibration_sheet(
        swatch_size,
        count_x,
        count_y,
        thickness,
        colors
) -> pv.Node:
    # center the whole sheet around the origin
    total_width  = swatch_size * count_x
    total_height = swatch_size * count_y

    union = pv.Union()

    for i in range(count_x):
        for j in range(count_y):
            # compute volume fractions
            c_frac = i / (count_x - 1) if count_x > 1 else 0
            m_frac = j / (count_y - 1) if count_y > 1 else 0
            w_frac = 1.0 - (c_frac + m_frac)
            fractions = [f"{c_frac:.3f}", f"{m_frac:.3f}", f"{w_frac:.3f}"]

            # compute the center of this swatch
            x_pos = -total_width/2 + swatch_size/2 + i * swatch_size
            y_pos = -total_height/2 + swatch_size/2 + j * swatch_size
            center = pv.Vec3(x_pos, y_pos, 0)

            base = pv.RectPrism(center, pv.Vec3(swatch_size, swatch_size, thickness), W)
            graded = pv.FGrade(
                fractions,
                [colors[0], colors[1], colors[2]],
                True,
                base
            )

            union.add_child(graded)

    return union


# Load some materials
mats = pv.default_materials
C = mats.id("cyan")
M = mats.id("magenta")
W = mats.id("white")

# Set Parameters
SWATCH_SIZE = 25    # mm
NX, NY      = 12, 12  # subdivisions
THICKNESS   = 10     # mm per layer
COLORS = [C,M,W]


root = create_color_calibration_sheet(
    swatch_size = SWATCH_SIZE,
    count_x     = NX,
    count_y     = NY,
    thickness   = THICKNESS,
    colors      = COLORS
)

viz.Render(root, mats)
