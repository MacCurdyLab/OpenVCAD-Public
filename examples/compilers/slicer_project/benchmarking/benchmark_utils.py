"""Shared configuration and utilities for slicer project benchmarks."""

import csv
import ctypes
import json
import os
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree

import pyvcad as pv

try:
    import fcntl
except ImportError:
    fcntl = None


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]

SUBMESH_COUNTS = [5, 12, 19, 26, 33, 40]
VOXEL_SIZE_MM = 0.5
VOXEL_SIZE = pv.Vec3(VOXEL_SIZE_MM, VOXEL_SIZE_MM, VOXEL_SIZE_MM)

BAR_SIZE_X = 200.0
BAR_SIZE_Y = 50.0
BAR_SIZE_Z = 50.0

OUTPUT_DIR = HERE / "output"
PLOTS_DIR = HERE / "plots"
COMPILER_CSV_PATH = HERE / "benchmarking.csv"
PRUSASLICER_CSV_PATH = HERE / "prusaslicer_benchmarking.csv"
PRUSASLICER_EXECUTABLE = Path(
    "/Applications/PrusaSlicer.app/Contents/MacOS/PrusaSlicer"
)

PROFILES_DIR = (
    REPO_ROOT / "examples" / "applications" / "foaming_filaments" / "profiles"
)
PRINTER_PROFILE_PATH = PROFILES_DIR / "prusa_xl_multitool.ini"
PLA_FILAMENT_PROFILE_PATH = PROFILES_DIR / "ColorFabb_LW_PLA.ini"

METHODS = {
    "settings_meshes": {
        "label": "Settings Meshes",
        "filename": "settings_meshes",
    },
    "virtual_extrusion": {
        "label": "Virtual Extrusion",
        "filename": "virtual_extrusion",
    },
    "half_toning": {
        "label": "Half-toning",
        "filename": "half_toning",
    },
}

COMPILER_CSV_FIELDS = [
    "method_id",
    "method",
    "requested_submeshes",
    "actual_submeshes",
    "elapsed_seconds",
    "voxel_size_mm",
    "bar_size_x_mm",
    "bar_size_y_mm",
    "bar_size_z_mm",
    "output_path",
    "output_bytes",
    "timestamp",
    "status",
    "error",
]

PRUSASLICER_CSV_FIELDS = [
    "method_id",
    "method",
    "requested_submeshes",
    "actual_submeshes",
    "elapsed_seconds",
    "input_path",
    "gcode_output_path",
    "prusa_slicer_path",
    "timestamp",
    "status",
    "return_code",
    "error",
]


def dimensions():
    return {
        "bar_size_x": BAR_SIZE_X,
        "bar_size_y": BAR_SIZE_Y,
        "bar_size_z": BAR_SIZE_Z,
    }


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def project_path(method_id, submeshes):
    filename = METHODS[method_id]["filename"]
    return OUTPUT_DIR / "{}_{:03d}.3mf".format(filename, submeshes)


def gcode_path(method_id, submeshes):
    filename = METHODS[method_id]["filename"]
    return OUTPUT_DIR / "{}_{:03d}.gcode".format(filename, submeshes)


def remove_obsolete_project_files(method_id):
    filename = METHODS[method_id]["filename"]
    expected_paths = {
        project_path(method_id, submeshes)
        for submeshes in SUBMESH_COUNTS
    }
    for path in OUTPUT_DIR.glob("{}_*.3mf".format(filename)):
        if path not in expected_paths:
            path.unlink()


def timestamp_utc():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def timed_compile(compiler):
    start = time.perf_counter()
    compiler.compile()
    return time.perf_counter() - start


def inspect_3mf(path):
    result = {"actual_submeshes": ""}
    path = Path(path)
    if not path.exists():
        return result

    with zipfile.ZipFile(path) as archive:
        config_name = "Metadata/Slic3r_PE_model.config"
        if config_name in archive.namelist():
            with archive.open(config_name) as handle:
                tree = ElementTree.parse(handle)
            result["actual_submeshes"] = str(len(tree.findall(".//volume")))
            return result

        report_name = "Metadata/OpenVCAD_prusa_colormix_report.json"
        if report_name in archive.namelist():
            with archive.open(report_name) as handle:
                data = json.load(handle)
            result["actual_submeshes"] = str(data.get("selected_count", ""))
    return result


def compiler_row(method_id, requested_submeshes, output_path):
    return {
        "method_id": method_id,
        "method": METHODS[method_id]["label"],
        "requested_submeshes": requested_submeshes,
        "voxel_size_mm": VOXEL_SIZE_MM,
        "bar_size_x_mm": BAR_SIZE_X,
        "bar_size_y_mm": BAR_SIZE_Y,
        "bar_size_z_mm": BAR_SIZE_Z,
        "output_path": str(output_path),
        "timestamp": timestamp_utc(),
    }


def mark_compile_success(row, elapsed_seconds, output_path):
    row["elapsed_seconds"] = "{:.9f}".format(elapsed_seconds)
    row["output_bytes"] = str(Path(output_path).stat().st_size)
    row.update(inspect_3mf(output_path))
    if row["actual_submeshes"] == "":
        raise RuntimeError(
            "Could not determine the emitted sub-mesh count in {}".format(output_path)
        )
    row["status"] = "ok"
    row["error"] = ""
    return row


def mark_error(row, error):
    row["status"] = "error"
    row["error"] = str(error)
    return row


def normalize_row(row, fieldnames):
    return {field: str(row.get(field, "")) for field in fieldnames}


def row_key(row):
    return (
        str(row.get("method_id", "")),
        str(row.get("requested_submeshes", "")),
    )


def write_replace_rows(csv_path, fieldnames, new_rows):
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = csv_path.with_suffix(csv_path.suffix + ".lock")

    with lock_path.open("w") as lock_handle:
        if fcntl is not None:
            fcntl.flock(lock_handle, fcntl.LOCK_EX)

        existing_rows = []
        if csv_path.exists():
            with csv_path.open("r", newline="") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames == fieldnames:
                    existing_rows.extend(reader)

        new_keys = {row_key(row) for row in new_rows}
        valid_submesh_counts = {str(value) for value in SUBMESH_COUNTS}
        rows = [
            row for row in existing_rows
            if row_key(row) not in new_keys
            and row.get("requested_submeshes", "") in valid_submesh_counts
        ]
        rows.extend(normalize_row(row, fieldnames) for row in new_rows)
        rows.sort(
            key=lambda row: (
                row.get("method_id", ""),
                int(row.get("requested_submeshes", 0)),
            )
        )

        fd, temporary_path = tempfile.mkstemp(
            prefix=csv_path.name + ".",
            suffix=".tmp",
            dir=str(csv_path.parent),
        )
        os.close(fd)
        try:
            with open(temporary_path, "w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(normalize_row(row, fieldnames) for row in rows)
            os.replace(temporary_path, csv_path)
        finally:
            if os.path.exists(temporary_path):
                os.remove(temporary_path)
            if fcntl is not None:
                fcntl.flock(lock_handle, fcntl.LOCK_UN)


def run_compiler_benchmark(method_id, build_design, build_compiler):
    ensure_output_dir()
    remove_obsolete_project_files(method_id)
    for submeshes in SUBMESH_COUNTS:
        output_path = project_path(method_id, submeshes)
        row = compiler_row(method_id, submeshes, output_path)
        try:
            if output_path.exists():
                output_path.unlink()
            root = build_design()
            compiler = build_compiler(root, output_path, submeshes)
            elapsed_seconds = timed_compile(compiler)
            mark_compile_success(row, elapsed_seconds, output_path)
        except Exception as exc:
            mark_error(row, exc)

        write_replace_rows(
            COMPILER_CSV_PATH,
            COMPILER_CSV_FIELDS,
            [row],
        )
        print(
            "{status}: {method} submeshes={submeshes}".format(
                status=row["status"],
                method=METHODS[method_id]["label"],
                submeshes=submeshes,
            )
        )

    print("Updated", COMPILER_CSV_PATH)


def prusaslicer_command(input_path, output_path):
    return [
        str(PRUSASLICER_EXECUTABLE),
        "--export-gcode",
        "--output",
        str(output_path),
        str(input_path),
    ]


def run_prusaslicer(input_path, output_path):
    command = prusaslicer_command(input_path, output_path)
    start = time.perf_counter()
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    elapsed_seconds = time.perf_counter() - start
    return result, elapsed_seconds


def preload_compiler_dependencies():
    if sys.platform != "darwin":
        return

    lib_path = (
        REPO_ROOT
        / "deps"
        / "macos"
        / "vcpkg_installed"
        / "arm64-osx"
        / "lib"
        / "lib3mf.2.4.1.0.dylib"
    )
    if lib_path.exists():
        ctypes.CDLL(str(lib_path), mode=ctypes.RTLD_GLOBAL)
