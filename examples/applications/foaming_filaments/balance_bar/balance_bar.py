import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_compilers as pvc
import pyvcad_attribute_resolver as resolver
import math

resolver.register_foaming_conversions()

# --- Configuration ---
bar_length = 200.0
bar_width = 10.0
bar_height = 10.0
x_half = bar_length / 2.0  # 100.0 mm

rho_min = 0.413
rho_max = 1.123

# DESIRED CENTER OF MASS (X in mm)
# Positive = Right, Negative = Left.
# Max theoretical shift is approx +/- 23.1 mm
target_x_com_mm = 24.4

def solve_balance_point(target_x, half_length, min_rho, max_rho):
    """
    Analytically solves for the exact boundary (balance point) between two regions 
    of density (min_rho and max_rho) to achieve the target Center of Mass.
    """
    if min_rho >= max_rho:
        raise ValueError("max_rho must be greater than min_rho")

    # Ratio used in the quadratic formula
    R = (max_rho + min_rho) / (max_rho - min_rho)
    
    # Calculate the theoretical max shift achievable with a pure step function
    max_shift = half_length * (R - math.sqrt(R**2 - 1))

    if abs(target_x) > max_shift:
        raise ValueError(f"Target {target_x} mm exceeds theoretical limit of +/- {max_shift:.3f} mm")

    # Absolute target center of mass
    xc = abs(target_x)
    
    # Quadratic formula derived from Center of Mass equation
    # We take the root that places the boundary within the bar
    b_pos = xc - math.sqrt(xc**2 - 2 * xc * half_length * R + half_length**2)

    # If the target is negative (shifted left), the boundary mirrors to the right
    if target_x < 0:
        return -b_pos
    
    return b_pos

def get_step_expression(target_x, balance_point, min_rho, max_rho):
    """Generates the piecewise expression string for pyvcad"""
    if target_x >= 0:
        # Shift right: left side is min_rho, right side is max_rho
        expression = f"x > {balance_point:.8f} ? {max_rho} : {min_rho}"
    else:
        # Shift left: left side is max_rho, right side is min_rho
        expression = f"x > {balance_point:.8f} ? {min_rho} : {max_rho}"

    print(f"DEBUG: Calculated exact boundary point: {balance_point:.5f} mm")
    print(f"DEBUG: Generated Step Expression: {expression}")
    return expression

# --- Execution ---

# 1. Solve for balance point
boundary_x = solve_balance_point(target_x_com_mm, x_half, rho_min, rho_max)

# 2. Generate Expression
density_formula = get_step_expression(target_x_com_mm, boundary_x, rho_min, rho_max)
density_attr = pv.FloatAttribute(density_formula)

# 3. Create Geometry
rect_prism = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(bar_length, bar_width, bar_height))
rect_prism.set_attribute(pv.DefaultAttributes.DENSITY, density_attr)

# --- Resolve attribute chain & render ---
root = resolver.adapt(rect_prism,
                      ["temperature", "flow_rate"],
                      tags=["foaming_tpu"])

viz.Render(root)

compiler = pvc.PrusaSlicerProjectCompiler(root, pv.Vec3(0.15,0.15,0.15),
                                     "balance_bar_tpu.3mf",
                                     2,
                                     "../profiles/prusa_mk4s_profile.ini",
                                     "../profiles/ColorFabb_VarioShore_TPU.ini")
compiler.compile()