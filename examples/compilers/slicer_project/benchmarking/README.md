# Slicer Project Benchmarks

This suite measures how OpenVCAD project compilation, exported 3MF size, and
downstream PrusaSlicer time scale with the number of generated partitions.

The three methods are:

- **Settings Meshes**: an infill-density gradient.
- **Virtual Extrusion**: a foaming PLA temperature gradient with derived flow
  rate.
- **Half-toning**: a functional RGB sweep exported with expanded Prusa
  ColorMix recipes.

Each method uses a 200 x 50 x 50 mm bar, a 0.5 mm voxel size, and requested
partition counts of 5, 12, 19, 26, 33, and 40. Configuration is stored as
hard-coded constants in `benchmark_utils.py`.

## 1. Export and Time the 3MF Projects

From the repository root, run:

```bash
./.venv/bin/python examples/compilers/slicer_project/benchmarking/benchmark_settings_mesh_infill.py
./.venv/bin/python examples/compilers/slicer_project/benchmarking/benchmark_virtual_extrusion_temperature.py
./.venv/bin/python examples/compilers/slicer_project/benchmarking/benchmark_half_toning.py
```

The scripts write 18 projects to `output/` and record OpenVCAD compile
wall-clock time, actual partition count, and 3MF byte size in
`benchmarking.csv`.

Each run replaces the existing output and CSV row for that method and requested
partition count.

## 2. Configure Every Project in PrusaSlicer

Open each generated 3MF project in PrusaSlicer. For every project:

1. Place and orient the object correctly on the build plate.
2. Select the printer, print, and filament profiles intended for the study.
3. Save the project over the original 3MF file in `output/`.

Use identical profiles and placement rules across all cases. Do not rerun a
compiler benchmark after this step unless you intend to discard and repeat the
manual PrusaSlicer setup, because compilation replaces the configured project.

## 3. Time PrusaSlicer

The slicer benchmark requires PrusaSlicer at:

```text
/Applications/PrusaSlicer.app/Contents/MacOS/PrusaSlicer
```

Run:

```bash
./.venv/bin/python examples/compilers/slicer_project/benchmarking/benchmark_prusaslicer.py
```

The script invokes PrusaSlicer with `--export-gcode`, measures complete
subprocess wall-clock time, and writes `prusaslicer_benchmarking.csv`. Generated
G-code is deleted after each measurement. Rerunning replaces the previous CSV
row for each method and requested partition count.

## 4. Generate the Publication Figure

Run:

```bash
./.venv/bin/python examples/compilers/slicer_project/benchmarking/data_processing.py
```

The `plots/` directory receives SVG, PDF, and PNG versions of a three-panel
figure:

1. Slicer Project compilation time.
2. PrusaSlicer wall-clock time.
3. Exported 3MF size.

All panels use the actual emitted number of partitions on the x-axis. The
processing script warns if requested and actual counts differ, or if manual
PrusaSlicer setup changes the detected count.
