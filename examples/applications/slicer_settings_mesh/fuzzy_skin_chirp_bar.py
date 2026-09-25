import math
from pathlib import Path

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

# Execution controls
render = True
export = True

# Bar geometry (mm). The X width is not set directly: it is solved for below so
# that a whole number of cycles fits between the object bounds, subject to this
# cap. Y and Z are free.
block_size_x_max = 245.0
block_size_y = 5.0
block_size_z = 25.0

# Oscillation shape.
#   "sawtooth" ramps min -> max and snaps back, so every traverse runs the same
#             direction and every region comes out the same width.
#   "triangle" ramps min -> max -> min, which halves the traverse count for a
#             given width and merges the two half-bands at each reversal into a
#             double-width region.
# Both hold a constant slope on every ramp, so the bands are evenly spaced in X.
waveform = "sawtooth"

# Fuzzy-skin thickness swing (mm) traversed by each ramp.
fuzzy_skin_thickness_min = 0.0
fuzzy_skin_thickness_max = 1.0

# Fixed fuzzy-skin point distance (mm). Held constant so that region width is
# the only variable under test. This is NOT set as an OpenVCAD attribute: the
# compiler segments every settings-mesh attribute it finds, so a constant one
# would still multiply the band count by num_regions. Set it by hand in the
# PrusaSlicer print profile instead.
fuzzy_skin_point_distance = 0.1

# Target printer scale. The sweep below is quoted in multiples of these.
nozzle_diameter = 0.4
layer_height = 0.2

# THE SWEPT VARIABLE (mm): the width of a single settings-mesh region at each
# end of the bar. The sweep runs down to the width at which a region is
# expected to stop reproducing a distinguishable fuzzy skin.
region_width_start = 4.0
region_width_end = 0.5

# Region width below which the fuzzy skin is expected to stop resolving. Used
# only for the printed report, so the sweep can be pushed past it on purpose.
expected_minimum_region = 1.0

# How the region width shrinks along X. "linear" gives an equal decrement of
# region width per mm of bar, so the swept variable is sampled uniformly and
# the failure point can be read straight off a position measurement.
# "logarithmic" gives an equal decrement per octave instead, which spends far
# more of the bar below the limit.
region_sweep_profile = "linear"

# PrusaSlicer project export. The voxel grid is deliberately anisotropic: the
# attribute varies along X only, so X gets the whole resolution budget. Y and Z
# only have to reproduce flat faces, so sampling them coarsely keeps the 3MF to
# a size PrusaSlicer can still open. X is kept fine enough that even the
# narrowest region is many voxels across, so any breakdown observed is a slicer
# or printer limit rather than a sampling artifact.
compiler_voxel_size_x = 0.1
compiler_voxel_size_y = 0.1
compiler_voxel_size_z = 0.1
num_regions = 7
output_directory_name = "output"
output_filename = f"fuzzy_skin_chirp_bar_{waveform}_{num_regions}.3mf"

# Region width -> wavelength. Both waveforms hold a constant slope on a ramp,
# so one band height (peak-to-peak / num_regions) always spans the same
# distance in X and every region in a ramp is identical. A sawtooth fits one
# ramp per cycle and a triangle fits two, which is the only difference:
#     region width = wavelength / (traverses_per_cycle * num_regions)
# Asking for a given region width is therefore just asking for a wavelength.
if waveform == "sawtooth":
    traverses_per_cycle = 1
elif waveform == "triangle":
    traverses_per_cycle = 2
else:
    raise ValueError(
        f"waveform must be \"sawtooth\" or \"triangle\", got \"{waveform}\"")

wavelength_start = traverses_per_cycle * num_regions * region_width_start
wavelength_end = traverses_per_cycle * num_regions * region_width_end
wavelength_delta = wavelength_end - wavelength_start

# Solve the bar width for whole cycles. The sweep runs over the normalized
# coordinate u = x / width, so the accumulated phase scales linearly with the
# width and the cycles completed per mm of bar is a constant that depends only
# on the two wavelengths. Take as many whole cycles as fit under the cap and
# then size the bar to land exactly on that count, so the wave starts and ends
# on an object bound instead of being cut off mid-ramp.
if abs(wavelength_delta) < 1e-12:
    cycles_per_mm = 1.0 / wavelength_start
elif region_sweep_profile == "linear":
    cycles_per_mm = math.log(wavelength_end / wavelength_start) / wavelength_delta
elif region_sweep_profile == "logarithmic":
    cycles_per_mm = ((1.0 - wavelength_start / wavelength_end)
                     / (wavelength_start
                        * math.log(wavelength_end / wavelength_start)))
else:
    raise ValueError(
        f"region_sweep_profile must be \"linear\" or \"logarithmic\", "
        f"got \"{region_sweep_profile}\"")

cycle_count = int(math.floor(block_size_x_max * cycles_per_mm))
if cycle_count < 1:
    raise ValueError(
        f"Not even one cycle fits in {block_size_x_max} mm at these region "
        f"widths. Lower region_width_start or num_regions.")
block_size_x = cycle_count / cycles_per_mm

# Center the bar in X and Y, with its base on Z = 0.
block_min_x = -0.5 * block_size_x
block_center = pv.Vec3(0.0, 0.0, 0.5 * block_size_z)
block_size = pv.Vec3(block_size_x, block_size_y, block_size_z)

# The sawtooth's snap-back sits exactly on the phase wrap, which the right-hand
# bound lands on. Clamping u a hair below 1 keeps that bound at the top of the
# final ramp instead of letting it wrap to the bottom and leave a one-voxel
# sliver of the lowest band on the end face.
x_normalized_max = 1.0 - 1e-9 if waveform == "sawtooth" else 1.0
x_normalized_expr = (
    f"clamp((x - ({block_min_x})) / ({block_size_x}), 0, {x_normalized_max})"
)

if abs(wavelength_delta) < 1e-12:
    # Degenerate case: a constant region width is just a plain periodic wave.
    phase_scale = 2.0 * math.pi * block_size_x / wavelength_start
    phase_expr = f"({phase_scale}) * {x_normalized_expr}"
elif region_sweep_profile == "linear":
    # lambda(u) = lambda_start + delta * u. Integrating the local spatial
    # frequency 2*pi / lambda(x) over x gives a logarithmic phase.
    phase_scale = 2.0 * math.pi * block_size_x / wavelength_delta
    phase_expr = (
        f"({phase_scale}) * "
        f"log(1 + ({wavelength_delta / wavelength_start}) * {x_normalized_expr})"
    )
else:
    # lambda(u) = lambda_start * (lambda_end / lambda_start) ** u.
    sweep_exponent = math.log(wavelength_end / wavelength_start)
    phase_scale = 2.0 * math.pi * block_size_x / (wavelength_start * sweep_exponent)
    phase_expr = (
        f"({phase_scale}) * "
        f"(1 - exp(({-sweep_exponent}) * {x_normalized_expr}))"
    )


def local_wavelength(u):
    if abs(wavelength_delta) < 1e-12:
        return wavelength_start
    if region_sweep_profile == "linear":
        return wavelength_start + wavelength_delta * u
    return wavelength_start * math.exp(
        math.log(wavelength_end / wavelength_start) * u)


# Unit waveform in [-1, 1], built from the swept phase above. Both start at -1
# for phase 0, so the bar opens on a thickness minimum and, because the phase
# closes on a whole multiple of 2*pi, ends on a ramp boundary too.
if waveform == "sawtooth":
    # 2 * frac(p / 2pi) - 1. The phase is non-negative by construction, so
    # frac() never sees the negative argument it would truncate toward zero.
    unit_wave_expr = (
        f"2 * frac((0.15915494309189535) * ({phase_expr})) - 1"
    )
else:
    # -(2/pi) * asin(cos(p)). The clamp only guards asin against a cos()
    # result landing an ulp outside [-1, 1].
    unit_wave_expr = (
        f"(-0.6366197723675814) * asin(clamp(cos({phase_expr}), -1, 1))"
    )

thickness_midpoint = 0.5 * (fuzzy_skin_thickness_max + fuzzy_skin_thickness_min)
thickness_amplitude = 0.5 * (fuzzy_skin_thickness_max - fuzzy_skin_thickness_min)

fuzzy_skin_thickness_expr = (
    f"{thickness_midpoint} + {thickness_amplitude} * ({unit_wave_expr})"
)

# Only the thickness is graded. The compiler bins it into num_regions bands and
# emits one settings-mesh volume per band, so the printed stripes get narrower
# as the sweep tightens. A sawtooth keeps every region a clean single width; a
# triangle merges the two half-bands at each interior reversal into a
# double-width region, which doubles as a landmark in the profilometer trace.
block = pv.RectPrism(block_center, block_size)
block.set_attribute(
    pv.DefaultAttributes.FUZZY_SKIN_THICKNESS,
    pv.FloatAttribute(fuzzy_skin_thickness_expr),
)

root = block

# A triangle's reversals merge two half-bands into one region; a sawtooth snaps
# between the extreme bands instead, so nothing merges.
traverse_count = traverses_per_cycle * cycle_count
if waveform == "sawtooth":
    region_count = num_regions * cycle_count
    merge_note = "no merges"
else:
    region_count = 2 * cycle_count * (num_regions - 1) + 1
    merge_note = f"{2 * cycle_count - 1} double width at a reversal"

# Design report: where along the bar the regions stop being printable.
print(f"Bar: {block_size_x:.3f} x {block_size_y} x {block_size_z} mm "
      f"(solved for {cycle_count} whole cycles, cap {block_size_x_max} mm)")
print(
    f"Waveform: {waveform}, region width {region_width_start} -> "
    f"{region_width_end} mm ({region_sweep_profile} sweep)"
)
print(f"Thickness: {fuzzy_skin_thickness_min} -> {fuzzy_skin_thickness_max} mm "
      f"in {num_regions} regions per traverse")
print(f"Bar holds {traverse_count} traverses, {region_count} regions "
      f"({merge_note})")
print()
print(f"{'x (mm)':>9}  {'region':>7}  {'/nozzle':>8}  {'fuzz pts':>9}  "
      f"{'traverse':>9}  {'wavelen':>8}")
for step in range(5):
    u = step / 4.0
    x_position = block_min_x + u * block_size_x
    wavelength = local_wavelength(u)
    region_width = wavelength / (traverses_per_cycle * num_regions)
    print(
        f"{x_position:9.1f}  {region_width:7.3f}  "
        f"{region_width / nozzle_diameter:8.2f}  "
        f"{region_width / fuzzy_skin_point_distance:9.1f}  "
        f"{wavelength / traverses_per_cycle:9.2f}  {wavelength:8.2f}"
    )
print()

# Position where a region first falls below the expected resolution limit.
low = min(region_width_start, region_width_end)
high = max(region_width_start, region_width_end)
if low <= expected_minimum_region <= high and abs(wavelength_delta) > 1e-12:
    if region_sweep_profile == "linear":
        u_limit = ((region_width_start - expected_minimum_region)
                   / (region_width_start - region_width_end))
    else:
        u_limit = (math.log(expected_minimum_region / region_width_start)
                   / math.log(region_width_end / region_width_start))
    print(
        f"Region width reaches the {expected_minimum_region} mm resolution "
        f"limit at x = {block_min_x + u_limit * block_size_x:.1f} mm "
        f"({100.0 * u_limit:.0f}% along the bar)."
    )
else:
    print(
        f"The {expected_minimum_region} mm resolution limit is outside the "
        f"swept range, so the bar does not bracket it."
    )
print()

if render:
    viz.Render(root)

if export:
    here = Path(__file__).resolve().parent
    output_dir = here / output_directory_name
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / output_filename

    compiler = pvc.PrusaSlicerProjectCompiler(
        root,
        pv.Vec3(
            compiler_voxel_size_x,
            compiler_voxel_size_y,
            compiler_voxel_size_z,
        ),
        str(output_path),
        num_regions,
    )

    def report_progress(progress):
        print(f"Slicer export progress: {progress * 100:.1f}%")

    compiler.set_progress_callback(report_progress)
    compiler.compile()
    print("Wrote", output_path)
    print(
        "In PrusaSlicer: enable fuzzy skin for Outside walls, set "
        f"fuzzy skin point distance to {fuzzy_skin_point_distance} mm, and use a "
        f"{nozzle_diameter} mm nozzle at {layer_height} mm layers."
    )
