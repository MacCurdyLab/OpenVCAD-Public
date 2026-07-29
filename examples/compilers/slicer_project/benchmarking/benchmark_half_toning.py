"""Benchmark Half-toning export through Prusa ColorMix."""

import benchmark_utils as bu
import half_toning_design as design

bu.preload_compiler_dependencies()
import pyvcad_compilers as pvc


def build_compiler(root, output_path, submeshes):
    return pvc.PrusaSlicerProjectCompiler(
        root,
        bu.VOXEL_SIZE,
        str(output_path),
        submeshes,
        enable_color_mix=True,
        color_mix_recipe_preset="expanded",
        max_palette_size=submeshes,
        min_component_percent=15,
        max_recipe_components=3,
        region_overlap_mm=0.2,
    )


bu.run_compiler_benchmark(
    "half_toning",
    design.build_design,
    build_compiler,
)
