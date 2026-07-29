"""
Simulation compiler - direct mechanical properties export
=========================================================

Builds a graded cantilever beam with scalar elastic properties and exports it
to both Abaqus INP and FEniCSx XDMF/HDF5.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

bar_length = 40.0
bar_width = 12.0
bar_height = 12.0
half_length = 0.5 * bar_length
half_height = 0.5 * bar_height

bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_length, bar_width, bar_height))
bar.set_attribute(
    pv.DefaultAttributes.MODULUS,
    pv.FloatAttribute(f"1200 + 800 * clamp((x + {half_length}) / {bar_length}, 0, 1)")
)
bar.set_attribute(
    pv.DefaultAttributes.POISSONS_RATIO,
    pv.FloatAttribute(f"0.20 + 0.15 * clamp((z + {half_height}) / {bar_height}, 0, 1)")
)
root = bar

direct_attributes = [
    pv.DefaultAttributes.MODULUS,
    pv.DefaultAttributes.POISSONS_RATIO
]

abaqus_settings = pvc.SimulationCompilerSettings()
abaqus_settings.output_directory = "output"
abaqus_settings.file_prefix = "mechanical_hex"
abaqus_settings.backend = pvc.SimulationBackend.ABAQUS_INP
abaqus_settings.mesh_kind = pvc.SimulationMeshKind.HEX
abaqus_settings.random_seed = 7
abaqus_settings.direct_attributes = direct_attributes

hex_settings = pvc.SimulationHexMeshSettings()
hex_settings.voxel_size = pv.Vec3(1.5, 1.5, 1.5)
abaqus_settings.hex_settings = hex_settings

fenics_settings = pvc.SimulationCompilerSettings()
fenics_settings.output_directory = "output"
fenics_settings.file_prefix = "mechanical_tet"
fenics_settings.backend = pvc.SimulationBackend.FENICSX_XDMF
fenics_settings.mesh_kind = pvc.SimulationMeshKind.TET
fenics_settings.random_seed = 7
fenics_settings.direct_attributes = direct_attributes

tet_settings = pvc.SimulationTetFixedMeshSettings()
tet_settings.facet_size = 0.75
tet_settings.facet_distance = 0.75
tet_settings.cell_size = 0.75
fenics_settings.tet_fixed_settings = tet_settings

abaqus_compiler = pvc.SimulationCompiler(root, abaqus_settings)
abaqus_compiler.compile()
print("Abaqus files:", abaqus_compiler.written_files())

fenics_compiler = pvc.SimulationCompiler(root, fenics_settings)
fenics_compiler.compile()
print("FEniCSx files:", fenics_compiler.written_files())

viz.Render(root)
