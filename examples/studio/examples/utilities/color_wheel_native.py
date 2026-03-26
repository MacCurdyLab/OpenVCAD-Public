import pyvcad as pv
import math

# Function to generate Python functions for each color's volume fraction calculation
def generate_color_functions(num_colors):
    functions = []
    for k in range(1, num_colors + 1):
        # Precompute the angular offset for this color
        angle_offset = (2 * math.pi * (k - 1)) / num_colors
        
        # Define a function for this color's volume fraction
        def color_function(theta, offset=angle_offset):
            return 0.5 + 0.5 * math.cos(theta - offset)
        
        # Append the function to the list
        functions.append(color_function)
    return functions

# Number of colors
num_colors = 5

# Generate Python functions for each color
color_functions = generate_color_functions(num_colors)

# Define material IDs for the corresponding volume fractions
color_ids = [1, 2, 3, 4, 5]

# Create geometry nodes
big_cyl = pv.Cylinder(pv.Vec3(0, 0, 0), 25, 3, 1)
small_cyl = pv.Cylinder(pv.Vec3(0, 0, 0), 8, 3, 1)

# Create the gradient node using Python functions
gradient = pv.FGrade(color_functions, color_ids, True)
gradient.set_child(big_cyl)

# Create a difference node
diff = pv.Difference()
diff.set_left(gradient)
diff.set_right(small_cyl)

# Define the root node
root = diff
