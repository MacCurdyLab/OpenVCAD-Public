"""Benchmark Virtual Extrusion export for a foaming PLA temperature bar."""

import benchmark_utils as bu
import virtual_extrusion_temperature_design as design

bu.preload_compiler_dependencies()
import pyvcad_compilers as pvc


def build_compiler(root, output_path, submeshes):
    return pvc.PrusaSlicerProjectCompiler(
        root,
        bu.VOXEL_SIZE,
        str(output_path),
        submeshes,
        str(bu.PRINTER_PROFILE_PATH),
        str(bu.PLA_FILAMENT_PROFILE_PATH),
    )


bu.run_compiler_benchmark(
    "virtual_extrusion",
    design.build_design,
    build_compiler,
)
