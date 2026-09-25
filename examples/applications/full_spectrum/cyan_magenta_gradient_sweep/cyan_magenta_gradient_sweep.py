"""
Cyan-magenta gradient palette-size sweep
========================================

Takes the cyan-to-magenta volume-fraction bar and sweeps N, the number of
discrete filament-mix recipes the exporter is allowed to quantize the
continuous gradient into. One PrusaSlicer ColorMix project and one Orca
FullSpectrum project are written per step, so the same design can be printed
at several transition resolutions and compared side by side. Each bar carries
its own N inset into its top face to keep the printed specimens identifiable.

Turning on photo_fixture adds what a single comparison photograph needs: a
pure-magenta foot under every bar as a fixed contrast reference, and a socket
plate, exported on its own as a plain mesh, that stands the whole sweep in a
line at a repeatable pitch so one DSLR frame catches every specimen.
"""
from pathlib import Path

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

# Execution controls
render = True
export_colormix = True
export_full_spectrum = False

# Bar geometry (mm). X carries the gradient while the bar is still flat, and
# the ramp runs the full length: 100% cyan on one end face, 100% magenta on the
# other, with no unmixed caps.
prism_length = 100.0
prism_width = 20.0
prism_height = 20.0

# Stand the bar up so the gradient runs along Z. Every printed layer then holds
# a single mix recipe, which is what a color-mixing FFF machine wants.
rotate_vertical = True

# THE SWEPT VARIABLE: the palette size handed to both exporters. The gradient
# is continuous in the tree, so N alone decides how many discrete mix recipes/
# the sliced part ends up with. Both exporters default to
# volume_fraction_palette_mode="uniform", which cuts the fraction range into N
# equal bins, so each region comes out prism_length / N tall. Pass "adaptive"
# instead to spend recipes where the samples cluster, at the cost of uneven
# regions unless N is a power of two.
num_regions_min = 3
num_regions_max = 30
num_regions_steps = 4

# PHOTO FIXTURE MODE. Adds a pure-magenta foot below the gradient on every bar
# and writes a socket plate that holds the whole sweep in one line, so a single
# frame captures every specimen against an identical background. The bars are
# still exported one project each; the plate is a separate plain mesh.
photo_fixture = True

# Contrast foot (mm). Sits below the cyan end of the ramp, so every bar carries
# a hard magenta-against-cyan edge at a known height for the analysis script to
# key on. socket_depth of it is swallowed by the plate, leaving the rest proud.
foot_length = 5.0

# Socket plate (mm). Clearance is per side, so a pocket comes out
# 2 * socket_clearance wider than the bar it holds. 0.025 per side is a snug
# push fit off a 0.4 mm nozzle; double it if the bars need persuading.
socket_depth = 3.0
socket_clearance = 0.025
socket_relief = 1.0
object_gap = 2.0
fixture_base_thickness = 5.0
fixture_end_margin = 3.0

# Plate sampling resolution. Coarser than the bars on purpose: an exact box SDF
# puts flat faces at their true position whatever the voxel size, so this only
# decides how far the pocket edges round over, and slight rounding helps the
# bars drop in.
fixture_voxel_size = 0.25

# Label inset into the top face (+Z after the upright rotation). The depth is
# doubled and the text is centred on the face plane, so exactly
# label_inset_depth of it bites into the bar - shallow enough that its floor is
# still within a percent of pure magenta. Four Arial Bold characters at this
# height span about 14 mm, which clears the 20 mm face.
label_height = 6.0
label_inset_depth = 0.6
label_font = "Arial"

# Sampling resolution. Isotropic because the label is a real 3D feature: Z has
# to resolve the inset depth and XY the glyph strokes.
export_voxel_size = 0.15
output_directory_name = "output"

# Physical filaments and the volume-fraction materials that map onto them.
filaments = [
    {"slot": 1, "color_hex": "#00FFFF"},
    {"slot": 2, "color_hex": "#FF00FF"},
]
volume_fraction_materials = {
    "cyan": 1,
    "magenta": 2,
}
min_component_percent = 1
max_recipe_components = 2
region_overlap_mm = 0.0

# Which step to open in the interactive viewer when the fixture is off. The
# viewer shows the authored continuous gradient rather than the exporter's
# quantized palette, so every step looks the same apart from its label.
render_num_regions = num_regions_max

if photo_fixture and not rotate_vertical:
    raise RuntimeError(
        "photo_fixture stands the bars in sockets, so it needs "
        "rotate_vertical = True."
    )

materials = pv.default_materials
if callable(materials):
    materials = materials()

foot = foot_length if photo_fixture else 0.0
bar_length = prism_length + foot

# The ramp always spans prism_length and the foot extends the bar below it. The
# clamp is what keeps the fractions legal, since the tree is sampled in a
# bandwidth around the surface and x runs slightly past both end faces.
half_length = 0.5 * bar_length
gradient_start_x = -half_length + foot

ramp_expr = f"clamp(0, (x - ({gradient_start_x})) / {prism_length}, 1)"
if foot > 0.0:
    # Below the ramp the comparison evaluates to 1, which max() promotes to
    # full magenta, leaving a hard edge against the cyan end of the gradient.
    magenta_fraction_expr = f"max({ramp_expr}, (x < ({gradient_start_x})))"
else:
    magenta_fraction_expr = ramp_expr
cyan_fraction_expr = f"1 - ({magenta_fraction_expr})"

voxel_size = pv.Vec3(export_voxel_size, export_voxel_size, export_voxel_size)
bandwidth = 6.0 * export_voxel_size

# Evenly spaced region counts, inclusive of both ends.
region_counts = [
    int(round(num_regions_min
              + (num_regions_max - num_regions_min) * i / (num_regions_steps - 1)))
    for i in range(num_regions_steps)
]


def build_bar(num_regions):
    """Graded bar with its N label inset into the top face."""
    prism = pv.RectPrism(
        pv.Vec3(0.0, 0.0, 0.0),
        pv.Vec3(bar_length, prism_width, prism_height),
    )
    prism.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        pv.VolumeFractionsAttribute(
            [
                (cyan_fraction_expr, materials.id("cyan")),
                (magenta_fraction_expr, materials.id("magenta")),
            ]
        ),
    )

    bar = pv.Rotate(0.0, 90.0, 0.0, prism) if rotate_vertical else prism

    # Text is authored in XY and extruded along Z, but VTK lays the glyphs out
    # rotated a half turn in that plane, so a 180 degree roll about Z sets them
    # upright when read from +Z - the direction the top face is seen from.
    label = pv.Text(
        f"N={num_regions:02d}",
        label_height,
        2.0 * label_inset_depth,
        pv.FontAspect.Bold,
        label_font,
    )
    label = pv.Rotate(0.0, 0.0, 180.0, label)

    # Place both pieces from their measured bounds: Rotate pivots about the
    # child's bounding-box center, so neither one sits where the authored
    # coordinates suggest.
    bar.prepare(voxel_size, bandwidth)
    label.prepare(voxel_size, bandwidth)
    bar_min, bar_max = bar.bounding_box()
    label_min, label_max = label.bounding_box()

    label = pv.Translate(
        0.5 * (bar_min.x + bar_max.x) - 0.5 * (label_min.x + label_max.x),
        0.5 * (bar_min.y + bar_max.y) - 0.5 * (label_min.y + label_max.y),
        bar_max.z - 0.5 * (label_min.z + label_max.z),
        label,
    )

    return pv.Difference(bar, label)


def socket_layout():
    """Socket footprint, pitch and X centers, measured off a real bar."""
    probe = build_bar(region_counts[0])
    probe.prepare(voxel_size, bandwidth)
    probe_min, probe_max = probe.bounding_box()

    bar_x = probe_max.x - probe_min.x
    bar_y = probe_max.y - probe_min.y

    # Pitch is measured bar to bar, so the printed wall between two pockets
    # comes out object_gap minus the two clearances that flank it.
    pitch = bar_x + object_gap
    span = (len(region_counts) - 1) * pitch
    centers = [-0.5 * span + i * pitch for i in range(len(region_counts))]

    return (bar_x + 2.0 * socket_clearance,
            bar_y + 2.0 * socket_clearance,
            pitch,
            span,
            centers)


def build_photo_fixture():
    """Socket plate that stands every bar upright, in line, at a fixed pitch."""
    socket_x, socket_y, _pitch, span, centers = socket_layout()

    plate_z = fixture_base_thickness + socket_depth
    plate = pv.RectPrism(
        pv.Vec3(0.0, 0.0, 0.5 * plate_z),
        pv.Vec3(span + socket_x + 2.0 * fixture_end_margin,
                socket_y + 2.0 * fixture_end_margin,
                plate_z),
    )
    # The plate only ever gets meshed, so this attribute is here to keep the
    # assembly preview well defined. A matte neutral jig is what a DSLR wants
    # under the specimens anyway.
    plate.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        pv.VolumeFractionsAttribute([("1", materials.id("darkgray"))]),
    )

    fixture = plate
    for center_x in centers:
        # The cutter overshoots the plate top so the pocket opens cleanly
        # instead of leaving coincident faces for the mesher to resolve.
        cutter_z = socket_depth + socket_relief
        socket = pv.RectPrism(
            pv.Vec3(center_x, 0.0, fixture_base_thickness + 0.5 * cutter_z),
            pv.Vec3(socket_x, socket_y, cutter_z),
        )
        fixture = pv.Difference(fixture, socket)

    return fixture


def build_photo_assembly():
    """Fixture with every bar seated in its socket, as the camera will see it."""
    _socket_x, _socket_y, _pitch, _span, centers = socket_layout()
    assembly = build_photo_fixture()

    for center_x, num_regions in zip(centers, region_counts):
        bar = build_bar(num_regions)
        bar.prepare(voxel_size, bandwidth)
        bar_min, bar_max = bar.bounding_box()
        assembly = pv.Union(
            assembly,
            pv.Translate(
                center_x - 0.5 * (bar_min.x + bar_max.x),
                -0.5 * (bar_min.y + bar_max.y),
                fixture_base_thickness - bar_min.z,
                bar,
            ),
        )

    return assembly


# Sweep report: the color step each export asks the slicer to reproduce. The
# ramp is linear and the palette bins are equal, so the step is just the
# gradient length over N. Whole-percent recipe rounding moves a boundary by a
# few tenths of a millimetre at most.
print(f"Bar: {bar_length} x {prism_width} x {prism_height} mm, "
      f"{prism_length} mm cyan -> magenta gradient")
if photo_fixture:
    print(f"Contrast foot: {foot_length} mm full magenta, "
          f"{foot_length - socket_depth} mm of it proud of the plate")
print(f"Exporting {len(region_counts)} projects per format, "
      f"N = {region_counts[0]} .. {region_counts[-1]}")
print()
print(f"{'N':>4}  {'step mm':>8}  {'step %':>7}")
for num_regions in region_counts:
    print(
        f"{num_regions:>4}  {prism_length / num_regions:8.2f}  "
        f"{100.0 / num_regions:7.2f}"
    )
print()

if render:
    if photo_fixture:
        viz.Render(build_photo_assembly(), materials)
    else:
        viz.Render(build_bar(render_num_regions), materials)

here = Path(__file__).resolve().parent
output_dir = here / output_directory_name

if export_colormix or export_full_spectrum or photo_fixture:
    output_dir.mkdir(exist_ok=True)

if photo_fixture:
    socket_x, socket_y, pitch, span, _centers = socket_layout()
    fixture_path = output_dir / "photo_fixture.3mf"

    # Materials are irrelevant for a jig, so it goes out through the plain mesh
    # path rather than a slicer project compiler.
    fixture_mesh = pv.SurfaceMesh(build_photo_fixture(), fixture_voxel_size)
    fixture_mesh.write_3mf(str(fixture_path))

    print(f"Fixture: {span + socket_x + 2.0 * fixture_end_margin:.2f} x "
          f"{socket_y + 2.0 * fixture_end_margin:.2f} x "
          f"{fixture_base_thickness + socket_depth:.2f} mm, "
          f"{len(region_counts)} sockets at {pitch:.2f} mm pitch")
    print(f"Sockets: {socket_x:.3f} x {socket_y:.3f} mm, {socket_depth} mm deep, "
          f"{socket_clearance} mm clearance per side")
    print("Wrote", fixture_path)
    print()

if export_colormix:
    for num_regions in region_counts:
        output_path = (
            output_dir / f"cyan_magenta_colormix_N{num_regions:02d}.3mf"
        )

        compiler = pvc.PrusaSlicerProjectCompiler(
            build_bar(num_regions),
            voxel_size,
            str(output_path),
            enable_color_mix=True,
            color_mix_filaments=filaments,
            total_physical_extruders=5,
            volume_fraction_materials=volume_fraction_materials,
            max_palette_size=num_regions,
            min_component_percent=min_component_percent,
            max_recipe_components=max_recipe_components,
            region_overlap_mm=region_overlap_mm,
        )

        def report_progress(progress, label=num_regions):
            print(f"  ColorMix N={label:02d} progress: {progress * 100:.1f}%")

        compiler.set_progress_callback(report_progress)
        compiler.compile()
        print("Wrote", output_path)

if export_full_spectrum:
    for num_regions in region_counts:
        output_path = (
            output_dir / f"cyan_magenta_full_spectrum_N{num_regions:02d}.3mf"
        )

        compiler = pvc.FullSpectrumSlicerProjectCompiler(
            build_bar(num_regions),
            voxel_size,
            str(output_path),
            filaments=filaments,
            volume_fraction_materials=volume_fraction_materials,
            max_palette_size=num_regions,
            min_component_percent=min_component_percent,
            max_recipe_components=max_recipe_components,
            region_overlap_mm=region_overlap_mm,
            orca_process_profile_path=(
                "0.10mm FastDetail @Prusa XL 5T 0.4.json"
            ),
            orca_default_filament_profile_path="Prusa Generic PLA @XL 5T",
        )

        def report_progress(progress, label=num_regions):
            print(
                f"  FullSpectrum N={label:02d} progress: "
                f"{progress * 100:.1f}%"
            )

        compiler.set_progress_callback(report_progress)
        compiler.compile()
        print("Wrote", output_path)
