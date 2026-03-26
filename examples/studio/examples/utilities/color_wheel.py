import pyvcad as pv

def generate_color_expressions_rhs(num_colors):
    expressions = []
    for k in range(1, num_colors + 1):
        angle_offset = f"(2 * pi * ({k - 1}) / {num_colors})"
        expression = f"0.5 + 0.5 * cos(theta - {angle_offset})"
        expressions.append(expression)
    return expressions

num_colors = 5
color_expressions = generate_color_expressions_rhs(num_colors)

color_ids = [1,2,3,4,5]

big_cyl = pv.Cylinder(pv.Vec3(0,0,0), 25,3,1)
small_cyl = pv.Cylinder(pv.Vec3(0,0,0), 8,3,1)

gradient = pv.FGrade(color_expressions, color_ids, True)
gradient.set_child(big_cyl)

diff = pv.Difference()
diff.set_left(gradient)
diff.set_right(small_cyl)

root = diff
