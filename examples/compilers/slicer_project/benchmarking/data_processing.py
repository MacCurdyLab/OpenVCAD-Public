"""Generate a publication figure from compiler and PrusaSlicer benchmarks."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import benchmark_utils as bu


OUTPUT_STEM = "slicer_project_benchmark"

COLORS = {
    "settings_meshes": "#28628f",
    "virtual_extrusion": "#b44b3b",
    "half_toning": "#34845b",
}

MARKERS = {
    "settings_meshes": "o",
    "virtual_extrusion": "s",
    "half_toning": "^",
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "axes.linewidth": 0.8,
    "figure.dpi": 180,
    "legend.fontsize": 9,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.08,
})


def load_successful_rows(csv_path, fieldnames):
    csv_path = Path(csv_path)
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)

    rows = []
    with csv_path.open("r", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != fieldnames:
            raise RuntimeError("Unexpected columns in {}".format(csv_path))
        for row in reader:
            if row.get("status") != "ok":
                continue
            try:
                row["requested_submeshes"] = int(row["requested_submeshes"])
                row["actual_submeshes"] = int(row["actual_submeshes"])
                row["elapsed_seconds"] = float(row["elapsed_seconds"])
                if "output_bytes" in row:
                    row["output_megabytes"] = float(row["output_bytes"]) / 1_000_000.0
            except (TypeError, ValueError):
                continue
            rows.append(row)
    return rows


def method_rows(rows, method_id):
    return sorted(
        [row for row in rows if row["method_id"] == method_id],
        key=lambda row: row["actual_submeshes"],
    )


def plot_metric(ax, rows, metric, ylabel):
    for method_id, method in bu.METHODS.items():
        series = method_rows(rows, method_id)
        if not series:
            continue
        ax.plot(
            [row["actual_submeshes"] for row in series],
            [row[metric] for row in series],
            color=COLORS[method_id],
            marker=MARKERS[method_id],
            linewidth=1.8,
            markersize=5.0,
            label=method["label"],
        )

    ax.set_xlabel("Number of partitions")
    ax.set_ylabel(ylabel)
    ax.grid(True, color="#c9ced3", linewidth=0.6, alpha=0.55)
    ax.set_axisbelow(True)


def warn_count_mismatches(compiler_rows, slicer_rows):
    compiler_lookup = {}
    for row in compiler_rows:
        key = (row["method_id"], row["requested_submeshes"])
        compiler_lookup[key] = row["actual_submeshes"]
        if row["actual_submeshes"] != row["requested_submeshes"]:
            print(
                "WARNING: {} requested {} partitions but exported {}.".format(
                    row["method"],
                    row["requested_submeshes"],
                    row["actual_submeshes"],
                )
            )

    for row in slicer_rows:
        key = (row["method_id"], row["requested_submeshes"])
        if row["actual_submeshes"] != row["requested_submeshes"]:
            print(
                "WARNING: {} requested {} partitions but the configured 3MF has {}.".format(
                    row["method"],
                    row["requested_submeshes"],
                    row["actual_submeshes"],
                )
            )
        compiled_count = compiler_lookup.get(key)
        if compiled_count is not None and compiled_count != row["actual_submeshes"]:
            print(
                "WARNING: {} requested {} changed from {} to {} partitions "
                "during manual PrusaSlicer setup.".format(
                    row["method"],
                    row["requested_submeshes"],
                    compiled_count,
                    row["actual_submeshes"],
                )
            )


compiler_rows = load_successful_rows(
    bu.COMPILER_CSV_PATH,
    bu.COMPILER_CSV_FIELDS,
)
slicer_rows = load_successful_rows(
    bu.PRUSASLICER_CSV_PATH,
    bu.PRUSASLICER_CSV_FIELDS,
)

if not compiler_rows:
    raise RuntimeError("No successful compiler benchmark rows found.")
if not slicer_rows:
    raise RuntimeError("No successful PrusaSlicer benchmark rows found.")

warn_count_mismatches(compiler_rows, slicer_rows)

figure, axes = plt.subplots(1, 3, figsize=(10.8, 3.25))
plot_metric(axes[0], compiler_rows, "elapsed_seconds", "Compile time (s)")
plot_metric(axes[1], slicer_rows, "elapsed_seconds", "PrusaSlicer time (s)")
plot_metric(axes[2], compiler_rows, "output_megabytes", "3MF size (MB)")

panel_titles = [
    "(a) Slicer Project Compilation Time",
    "(b) Slice Time",
    "(c) .3MF Project File Size",
]
for ax, title in zip(axes, panel_titles):
    ax.set_title(title)

handles, labels = axes[0].get_legend_handles_labels()
figure.legend(
    handles,
    labels,
    loc="upper center",
    ncol=3,
    frameon=False,
    bbox_to_anchor=(0.5, 1.03),
)
figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.91))

bu.PLOTS_DIR.mkdir(parents=True, exist_ok=True)
for extension in ["svg", "pdf", "png"]:
    figure.savefig(bu.PLOTS_DIR / "{}.{}".format(OUTPUT_STEM, extension))
plt.close(figure)

print("Wrote plots to", bu.PLOTS_DIR)
