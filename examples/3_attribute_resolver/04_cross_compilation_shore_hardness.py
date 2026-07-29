"""
Cross-compilation from shore hardness
=====================================

One shore-hardness field can target multiple manufacturing backends. This demo
adapts the same design-intent gradient to:

1. foaming TPU virtual extrusion for PrusaSlicerProjectCompiler
2. J750 volume fractions for MaterialInkjetCompiler
"""
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyvcad as pv
import pyvcad_attribute_resolver as resolver
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.j750_materials

bar_length = 100.0
bar_width = 30.0
bar_height = 10.0

# Use the overlap between the two target models so the same design-intent field
# can be compiled without clamping on either backend.
shore_min = 65.0
shore_max = 86.0
shore_span = shore_max - shore_min
shore_expr = (
    f"max(min(({shore_span:.8f} * (x + {bar_length / 2.0:.8f}) / {bar_length:.8f}) + "
    f"{shore_min:.8f}, {shore_max:.8f}), {shore_min:.8f})"
)


def make_shore_hardness_bar():
    # The same geometric source model is reused for both compiler targets.
    bar = pv.RectPrism(pv.Vec3(0.0, 0.0, 0.0), pv.Vec3(bar_length, bar_width, bar_height))
    bar.set_attribute(
        pv.DefaultAttributes.SHORE_HARDNESS,
        pv.FloatAttribute(shore_expr),
    )
    return bar

bar = make_shore_hardness_bar()

# Target 1: foaming TPU on filament hardware -> temperature + flow_rate
resolver.clear_conversions()
resolver.register_tpu_conversions()
bar = resolver.adapt(
    bar,
    ["temperature", "flow_rate"],
    tags=["foaming_tpu"],
)

# Target 2: J750 inkjet hardware -> volume fractions
resolver.clear_conversions()
resolver.register_j750_shore_hardness_conversions(
    material_defs=materials,
    agilus_material="Agilus30Mgn",
    vero_material="VeroYellow",
)
bar = resolver.adapt(
    bar,
    ["volume_fractions"],
    tags=["j750_shore_hardness"],
)

here = Path(__file__).resolve().parent
output_dir = here / "output"
output_dir.mkdir(exist_ok=True)

soft_material_id = materials.id("Agilus30Mgn")
rigid_material_id = materials.id("VeroYellow")


def sample_gradient_profile(root, sample_count):
    root.prepare(pv.Vec3(1.0, 1.0, 1.0), 1.0)
    bbox_min, bbox_max = root.bounding_box()
    x_values = np.linspace(bbox_min.x, bbox_max.x, sample_count)

    shore_values = []
    temperature_values = []
    flow_rate_values = []
    soft_fraction_values = []
    rigid_fraction_values = []

    for x in x_values:
        signed_distance, samples = root.sample(float(x), 0.0, 0.0)
        if signed_distance is None or samples is None:
            raise RuntimeError("Failed to sample the bar at x={:.3f}.".format(x))

        shore_values.append(samples.get_sample(pv.DefaultAttributes.SHORE_HARDNESS))
        temperature_values.append(samples.get_sample(pv.DefaultAttributes.TEMPERATURE))
        flow_rate_values.append(samples.get_sample(pv.DefaultAttributes.FLOW_RATE))

        fractions = samples.get_sample(pv.DefaultAttributes.VOLUME_FRACTIONS)
        soft_fraction_values.append(fractions.get(soft_material_id, 0.0))
        rigid_fraction_values.append(fractions.get(rigid_material_id, 0.0))

    return {
        "x": x_values,
        "shore": shore_values,
        "temperature": temperature_values,
        "flow_rate": flow_rate_values,
        "soft_fraction": soft_fraction_values,
        "rigid_fraction": rigid_fraction_values,
    }


def plot_shore_comparison(ax, x_values, shore_values, other_series, title, other_ylabel):
    shore_line, = ax.plot(
        x_values,
        shore_values,
        color="#1f4e79",
        linewidth=2.2,
        label="Shore Hardness",
    )
    ax.set_title(title)
    ax.set_xlabel("X location along bar (mm)")
    ax.set_ylabel("Shore Hardness (A)")
    ax.grid(True, alpha=0.25)

    other_ax = ax.twinx()
    lines = [shore_line]
    for label, values, color in other_series:
        line, = other_ax.plot(
            x_values,
            values,
            color=color,
            linewidth=2.0,
            linestyle="--",
            label=label,
        )
        lines.append(line)

    other_ax.set_ylabel(other_ylabel)
    ax.legend(lines, [line.get_label() for line in lines], loc="best")


def plot_process_comparison(ax, profile):
    x_values = profile["x"]
    shore_line, = ax.plot(
        x_values,
        profile["shore"],
        color="#1f4e79",
        linewidth=2.2,
        label="Shore Hardness",
    )
    ax.set_title("Shore Hardness vs Temperature and Flow Rate")
    ax.set_xlabel("X location along bar (mm)")
    ax.set_ylabel("Shore Hardness (A)")
    ax.grid(True, alpha=0.25)

    temperature_ax = ax.twinx()
    temperature_line, = temperature_ax.plot(
        x_values,
        profile["temperature"],
        color="#b23a48",
        linewidth=2.0,
        linestyle="--",
        label="Temperature",
    )
    temperature_ax.set_ylabel("Temperature (C)")

    flow_rate_ax = ax.twinx()
    flow_rate_ax.spines["right"].set_position(("axes", 1.16))
    flow_rate_line, = flow_rate_ax.plot(
        x_values,
        profile["flow_rate"],
        color="#2a9d8f",
        linewidth=2.0,
        linestyle=":",
        label="Flow Rate",
    )
    flow_rate_ax.set_ylabel("Flow Rate Multiplier")

    lines = [shore_line, temperature_line, flow_rate_line]
    ax.legend(lines, [line.get_label() for line in lines], loc="best")


profile = sample_gradient_profile(bar, 1001)

fig, axes = plt.subplots(2, 1, figsize=(6, 8), constrained_layout=True)
plot_process_comparison(axes[0], profile)
plot_shore_comparison(
    axes[1],
    profile["x"],
    profile["shore"],
    [
        ("Rigid VeroYellow", profile["rigid_fraction"], "#e9c46a"),
        ("Soft Agilus30Mgn", profile["soft_fraction"], "#6a4c93"),
    ],
    "Shore Hardness vs Rigid/Soft Volume Fractions",
    "Volume Fraction",
)

plot_output_path = output_dir / "cross_compilation_shore_hardness_profiles.svg"
fig.savefig(plot_output_path)
plt.close(fig)
print("Wrote", plot_output_path)

# Render
viz.Render(bar, materials)

export = True
if export:
    # The slicer backend needs process attributes instead of hardness directly.
    profiles_dir = here.parent / "applications" / "foaming_filaments" / "profiles"
    printer_profile_path = profiles_dir / "prusa_mk4s_profile.ini"
    filament_profile_path = profiles_dir / "ColorFabb_VarioShore_TPU.ini"

    slicer_output_path = output_dir / "cross_compilation_shore_hardness_tpu.3mf"
    slicer_compiler = pvc.PrusaSlicerProjectCompiler(
        bar,
        pv.Vec3(0.25, 0.25, 0.25),
        str(slicer_output_path),
        10,
        str(printer_profile_path),
        str(filament_profile_path),
    )
    slicer_compiler.compile()
    print("Wrote", slicer_output_path)

    # The inkjet backend consumes the resolved J750 material volume fractions.
    inkjet_output_dir = output_dir / "cross_compilation_shore_hardness_j750_slices"
    if inkjet_output_dir.is_dir():
        shutil.rmtree(inkjet_output_dir)
    inkjet_output_dir.mkdir(exist_ok=True)

    inkjet_compiler = pvc.MaterialInkjetCompiler(
        bar,
        pv.Vec3(0.0423,0.0846,0.027),
        str(inkjet_output_dir),
        "slice_",
        materials,
        0.0,
    )
    inkjet_compiler.compile()
    print("Wrote", inkjet_output_dir)
