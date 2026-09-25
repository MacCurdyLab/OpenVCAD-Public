# Simulation-driven design studies

These two deterministic studies demonstrate the Task 2 feedback boundary:
an OpenVCAD source node is compiled to an in-memory TET4
`SimulationModel`, DOLFINx solves on a mesh constructed directly from those
arrays, and projected point results return through public
`UnstructuredFieldDataset` attributes. They are intentionally deeper and more
expensive than ordinary OpenVCAD examples. They do not introduce FEniCSx,
PETSc, MPI, or study-only visualization packages into OpenVCAD's normal
dependencies.

Generated meshes, XDMF/HDF5 bundles, solver logs, metrics, and headless images
are written beneath `.tmp/simulation_driven_design/` and must not be committed.

## Solver-neutral public import examples

The Advanced guide starts with two independent public-API examples before the
FEniCSx studies. Array construction needs only the normal repository virtual
environment:

```bash
./.venv/bin/python examples/applications/simulation_driven_design/03_array_result_import.py
```

The XDMF/HDF5 example uses `SimulationCompiler` to generate a supported TET4
bundle, augments it with analytic result fields through `h5py`, and loads the
result using only public OpenVCAD APIs. The pinned study environment already
contains `h5py`:

```bash
conda run -n openvcad-fenicsx python examples/applications/simulation_driven_design/04_xdmf_result_import.py
```

Neither example imports the FEniCSx solver or private study helpers.

## Reproducible environment

The checked-in environment pins the locally validated DOLFINx stack. From the
repository root:

```bash
conda env create --file examples/applications/simulation_driven_design/environment.yml
conda env update --name openvcad-fenicsx --file examples/applications/simulation_driven_design/environment.yml --prune
```

Install the local editable packages into that isolated environment. On macOS,
select AppleClang explicitly; this avoids conda compiler interception during
the OpenVCAD CMake thread probe:

```bash
conda run -n openvcad-fenicsx env CC=/usr/bin/clang CXX=/usr/bin/clang++ CMAKE_OSX_ARCHITECTURES=arm64 python -m pip install -e .
conda run -n openvcad-fenicsx python -m pip install -e rendering -e metamaterials
```

On Linux, the core editable install can normally use the environment compiler:

```bash
conda run -n openvcad-fenicsx python -m pip install -e .
conda run -n openvcad-fenicsx python -m pip install -e rendering -e metamaterials
```

Install normal OpenVCAD Python dependencies first if they are not already
present; the commands above let pip install them into a new environment.
An explicit `--no-deps` form is useful when verifying that this file alone
owns the solver stack.

Native Windows is not supported by the conda-forge DOLFINx build used here;
use Linux under WSL2. The entry points currently reject `MPI.COMM_WORLD` sizes
greater than one. Input-global point IDs and original-cell IDs are validated in
serial, but an MPI execution command is deliberately not advertised because
the complete study has not been validated under `mpirun`.

## One-command execution

Study 1 performs exactly one baseline structural solve and exactly one
verification structural solve. Study 2 performs one solid-envelope solve and
does not solve the lattice:

```bash
conda run -n openvcad-fenicsx python examples/applications/simulation_driven_design/01_cantilever_material_feedback.py
conda run -n openvcad-fenicsx python examples/applications/simulation_driven_design/02_bcc_radius_feedback.py
```

Fast mode retains compilation, ordering checks, structural solves, projection,
Task 1 import, coverage preflight, feedback, metrics, bundles, and rendering,
while reducing TET4 and render/lattice-volume resolution:

```bash
conda run -n openvcad-fenicsx python examples/applications/simulation_driven_design/01_cantilever_material_feedback.py --fast
conda run -n openvcad-fenicsx python examples/applications/simulation_driven_design/02_bcc_radius_feedback.py --fast
```

`--no-render` is available for solver-only checks. On the validated Apple
Silicon workstation, fast mode is expected to complete in under 3 minutes and
under 2 GB per study; default mode is expected to complete in under 10 minutes
and under 4 GB per study. Rendering dominates Study 2. Actual timings are
recorded in each `metrics.json`.

Run the public-loader smoke independently after Study 1:

```bash
conda run -n openvcad-fenicsx python examples/applications/simulation_driven_design/public_loader_smoke.py
```

The smoke script imports no study helper. It uses only public `pyvcad` APIs to
list fields and associations, create a `FloatAttribute` and `Vec3Attribute`,
sample known tetrahedron-interior points, and report coverage.

The separate stability validation intentionally runs two complete Study 1
cases (four structural solves total) so the main one-command path can retain
its exactly-one-baseline/exactly-one-verification contract:

```bash
conda run -n openvcad-fenicsx python examples/applications/simulation_driven_design/validate_resolution_stability.py
```

## Study 1 formulation and feedback

The source is a 30 x 6 x 6 mm OpenVCAD cantilever, fixed on the x-min end and
loaded by a uniform `(0, 0, -0.0005)` MPa traction on the x-max end. The solver
uses a Taylor-Hood P2 displacement/P1 pressure mixed formulation. Its
deviatoric displacement-pressure split avoids the volumetric locking of a
displacement-only P1 tetrahedron at the Agilus30 endpoint, `nu = 0.49`.

The study uses these settled endpoints:

| Material | E (MPa) | nu | Density reference (g/cm3) |
| --- | ---: | ---: | ---: |
| Agilus30 | 1.265 | 0.49 | 1.145 |
| Vero | 2500 | 0.35 | 1.18 |

Sources: [Stratasys Agilus30 data
sheet](https://www.stratasys.com/contentassets/b05149b154d9485cb8f0763b53398eb4/mds_pj_agilus30_cmy_a4_1122a.pdf),
[Stratasys Vero data
sheet](https://www.stratasys.com/siteassets/materials/materials-catalog/polyjet-materials/verovivid/mds_pj_vero_for_j55_0320a.pdf),
and the [University of Maryland linearized Agilus30/VeroWhite property
table](https://api.drum.lib.umd.edu/server/api/core/bitstreams/7ff304c1-7689-469e-935f-22b67463be8a/content).
Agilus30 is actually nonlinear, viscoelastic, rate-dependent, and capable of
large strains. These linearized constants are a controlled small-strain
workflow simplification.

Strain-energy density is L2-projected into a continuous CG1 point field. Small
negative nodal overshoots from projection are reported and clamped to the
physical lower bound zero. The 5th and 95th nodal percentiles define robust
normalization bounds. A monotonic logistic allocation with named sharpness
`8.0` solves its offset by bisection until the lumped-TET-volume mean Vero
fraction equals the named `0.35` budget within `1e-8`.

The Vero field is attached to the retained source geometry, then converted to
Agilus30/Vero fractions through `VolumeFractionsExpressionConverter` and
`AttributeModifier`. Verification properties use an isolated linear mixture
of E and nu at cell centroids. This rule demonstrates the feedback workflow;
it is not a calibrated PolyJet digital-material model. A production workflow
must replace it with measured composition-to-property curves.

## Study 2 geometry control

The source is a 36 x 12 x 12 mm solid envelope, fixed on its x-min end and
loaded over the upper half of its x-max end to create a visibly nonuniform
energy field. The projected field follows the same Task 1 import and bounded
coverage path. Robustly normalized energy maps directly from a
`FloatAttribute` into a BCC beam/node radius of 0.55 to 1.30 mm. Both the raw
energy and final radius are attached as named attributes.

Constant and result-driven lattices use the same envelope, cell counts,
camera, clipping plane, image resolution, and fixed 0.55-to-1.30 mm scalar
range. Material usage is estimated from both implicit lattices at the same
voxel resolution and the relative difference is recorded. No lattice FEA
verification solve is included in Task 2.

## Validation artifacts

Each study writes `metrics.json`, `solver.log`, a supported XDMF/HDF5 bundle,
and its PNG renders beneath its own output directory. Metrics include mesh and
global-index checks, convergence reasons, displacement, compliance and strain
energy, projection bounds, raw/clamped coverage, maximum clamp distance,
allocation/radius ranges, budget, and material-usage estimates. Open the XDMF
files in ParaView for optional field inspection.
