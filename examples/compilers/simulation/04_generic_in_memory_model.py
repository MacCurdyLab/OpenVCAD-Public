"""
Simulation compiler - generic in-memory model
=============================================

Compiles one attribute-rich OpenVCAD object into solver-neutral HEX8 and TET4
models without creating intermediary files. The returned arrays can be passed
directly to Python analysis, solver, or serialization code.
"""

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

bar_length = 30.0
bar = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(bar_length, 10.0, 10.0),
)
bar.set_attribute(
    pv.DefaultAttributes.MODULUS,
    pv.FloatAttribute(
        f"1000 + 1000 * clamp((x + {0.5 * bar_length}) / {bar_length}, 0, 1)"
    ),
)
root = bar

hex_settings = pvc.SimulationCompilerSettings()
hex_settings.backend = pvc.SimulationBackend.GENERIC
hex_settings.mesh_kind = pvc.SimulationMeshKind.HEX
hex_settings.direct_attributes = [pv.DefaultAttributes.MODULUS]
hex_mesh_settings = pvc.SimulationHexMeshSettings()
hex_mesh_settings.voxel_size = pv.Vec3(1.0, 1.0, 1.0)
hex_settings.hex_settings = hex_mesh_settings

hex_compiler = pvc.SimulationCompiler(root, hex_settings)
hex_compiler.compile()
hex_model = hex_compiler.model()

tet_settings = pvc.SimulationCompilerSettings()
tet_settings.backend = pvc.SimulationBackend.GENERIC
tet_settings.mesh_kind = pvc.SimulationMeshKind.TET
tet_settings.random_seed = 7
tet_settings.direct_attributes = [pv.DefaultAttributes.MODULUS]
tet_mesh_settings = pvc.SimulationTetFixedMeshSettings()
tet_mesh_settings.facet_size = 1.5
tet_mesh_settings.facet_distance = 0.25
tet_mesh_settings.cell_size = 1.5
tet_settings.tet_fixed_settings = tet_mesh_settings

tet_compiler = pvc.SimulationCompiler(root, tet_settings)
tet_compiler.compile()
tet_model = tet_compiler.model()

for name, compiler, model in (
    ("hex", hex_compiler, hex_model),
    ("tet", tet_compiler, tet_model),
):
    element_count = len(model.connectivity) // model.nodes_per_cell
    first_element = model.connectivity[: model.nodes_per_cell]
    print(
        f"{name}: cell_type={model.cell_type}, nodes={len(model.nodes)}, "
        f"elements={element_count}, first_element={first_element}"
    )
    print("  modulus samples:", model.scalar_fields["modulus"][:3])
    print("  written files:", compiler.written_files())

viz.Render(root)
