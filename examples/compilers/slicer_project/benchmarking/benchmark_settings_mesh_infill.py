"""Benchmark Settings Meshes export for an infill-density bar."""

import benchmark_utils as bu
import settings_mesh_infill_design as design

bu.preload_compiler_dependencies()
import pyvcad_compilers as pvc


def build_compiler(root, output_path, submeshes):
    return pvc.PrusaSlicerProjectCompiler(
        root,
        bu.VOXEL_SIZE,
        str(output_path),
        submeshes,
    )


bu.run_compiler_benchmark(
    "settings_meshes",
    design.build_design,
    build_compiler,
)
