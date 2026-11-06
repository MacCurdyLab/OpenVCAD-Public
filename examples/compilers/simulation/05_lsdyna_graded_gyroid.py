"""
Simulation compiler - LS-DYNA keyword export
============================================

Builds a small gyroid block whose walls thicken along x and whose material
blends from a soft to a stiff polymer along z, then exports it as an LS-DYNA
keyword deck (.k) made of linear tetrahedra.

The deck is geometry only: nodes, solid elements, one part per material,
placeholder *MAT_ELASTIC cards and part sets. Units are mm, tonne, s, N, MPa.
Decks like this one were checked with LS-DYNA R16.1 (SMP, double precision):
they read, initialise and run a short explicit test. Review the deck and
replace the placeholder materials before real use.
"""
import os

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

script_dir = os.path.dirname(os.path.abspath(__file__))

# The material table names the two parts. Its optional density (tonne/mm^3),
# modulus (MPa) and poissons_ratio entries fill the placeholder *MAT_ELASTIC
# cards; materials without them get the writer defaults.
materials = pv.MaterialDefs(os.path.join(script_dir, "lsdyna_materials.json"))

block_min = pv.Vec3(-10.0, -10.0, -5.0)
block_max = pv.Vec3(10.0, 10.0, 5.0)
cell_map = mm.rectangular_cell_map((block_min, block_max), cells=(2, 2, 1))

# Gyroid walls grow from 0.8 mm at x = -10 to 2.0 mm at x = +10.
wall_thickness = pv.FloatAttribute("0.8 + 1.2 * (x + 10.0) / 20.0")
gyroid = mm.gyroid(cell_map, wall_thickness=wall_thickness)

# Soft polymer at the bottom (z = -5), stiff polymer at the top (z = +5).
gyroid.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute(
        [
            ("1 - clamp((z + 5.0) / 10.0, 0, 1)", materials.id("soft_polymer")),
            ("clamp((z + 5.0) / 10.0, 0, 1)", materials.id("stiff_polymer")),
        ]
    ),
)
root = gyroid

tet_settings = pvc.SimulationTetFixedMeshSettings()
tet_settings.facet_size = 0.6
tet_settings.facet_distance = 0.1
tet_settings.cell_size = 0.6

settings = pvc.SimulationCompilerSettings()
settings.output_directory = os.path.join(script_dir, "output")
settings.file_prefix = "graded_gyroid"
settings.backend = pvc.SimulationBackend.LSDYNA_K
settings.mesh_kind = pvc.SimulationMeshKind.TET
settings.tet_fixed_settings = tet_settings
settings.random_seed = 7
settings.material_defs = materials

# LS-DYNA options: tets are written as degenerate 8-node solids. ELFORM 13 is
# the default, but the two polymers have different bulk moduli and share
# nodes, which ELFORM 13 does not allow, so this deck gets
# mixed_material_tet_element_formulation (ELFORM 10). Void elements are
# dropped by default.
settings.lsdyna_settings.title = "OpenVCAD graded gyroid block"
settings.lsdyna_settings.tet_element_formulation = 13
settings.lsdyna_settings.mixed_material_tet_element_formulation = 10

compiler = pvc.SimulationCompiler(root, settings)
compiler.compile()
print("LS-DYNA deck:", compiler.written_files())
print("Nodes:", compiler.node_count(), "Elements:", compiler.element_count())

viz.Render(root, materials)
