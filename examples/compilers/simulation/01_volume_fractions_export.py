"""
Simulation compiler - volume fractions export
=============================================

Builds a bar with a left-to-right volume-fraction gradient and exports the
design to Abaqus INP plus both high- and low-resolution FEniCSx XDMF/HDF5
meshes using the simulation compiler.
"""
import os
import shutil

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.default_materials

bar_length = 30.0
bar_width = 10.0
bar_height = 10.0
half_length = 0.5 * bar_length

bar = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(bar_length, bar_width, bar_height))
fractions = pv.VolumeFractionsAttribute(
    [
        (f"1 - clamp((x + {half_length}) / {bar_length}, 0, 1)", materials.id("red")),
        (f"clamp((x + {half_length}) / {bar_length}, 0, 1)", materials.id("blue"))
    ]
)
bar.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS, fractions)
root = bar

hex_settings = pvc.SimulationHexMeshSettings()
hex_settings.voxel_size = pv.Vec3(0.25, 0.25, 0.25)

abaqus_settings = pvc.SimulationCompilerSettings()
abaqus_settings.output_directory = "output"
abaqus_settings.file_prefix = "volume_fractions_hex"
abaqus_settings.backend = pvc.SimulationBackend.ABAQUS_INP
abaqus_settings.mesh_kind = pvc.SimulationMeshKind.HEX
abaqus_settings.hex_settings = hex_settings
abaqus_settings.random_seed = 42
abaqus_settings.material_defs = materials

high_fenics_settings = pvc.SimulationCompilerSettings()
high_fenics_settings.output_directory = "output"
high_fenics_settings.file_prefix = "volume_fractions_tet_high"
high_fenics_settings.backend = pvc.SimulationBackend.FENICSX_XDMF
high_fenics_settings.mesh_kind = pvc.SimulationMeshKind.TET
high_fenics_settings.random_seed = 42
high_fenics_settings.material_defs = materials

high_tet_settings = pvc.SimulationTetFixedMeshSettings()
high_tet_settings.facet_size = 0.75
high_tet_settings.facet_distance = 0.5
high_tet_settings.cell_size = 0.75
high_fenics_settings.tet_fixed_settings = high_tet_settings

low_fenics_settings = pvc.SimulationCompilerSettings()
low_fenics_settings.output_directory = "output"
low_fenics_settings.file_prefix = "volume_fractions_tet_low"
low_fenics_settings.backend = pvc.SimulationBackend.FENICSX_XDMF
low_fenics_settings.mesh_kind = pvc.SimulationMeshKind.TET
low_fenics_settings.random_seed = 42
low_fenics_settings.material_defs = materials

low_tet_settings = pvc.SimulationTetFixedMeshSettings()
low_tet_settings.facet_size = 2.25
low_tet_settings.facet_distance = 1.5
low_tet_settings.cell_size = 2.25
low_fenics_settings.tet_fixed_settings = low_tet_settings

abaqus_compiler = pvc.SimulationCompiler(root, abaqus_settings)
abaqus_compiler.compile()
print("Abaqus files:", abaqus_compiler.written_files())

high_fenics_compiler = pvc.SimulationCompiler(root, high_fenics_settings)
high_fenics_compiler.compile()
print("High-resolution FEniCSx files:", high_fenics_compiler.written_files())

low_fenics_compiler = pvc.SimulationCompiler(root, low_fenics_settings)
low_fenics_compiler.compile()
print("Low-resolution FEniCSx files:", low_fenics_compiler.written_files())

viz.Render(root, materials)
