# 3MF Beam Lattice Sample Files

These files are the official 3MF Consortium beam lattice samples, taken unmodified from
[3MFConsortium/3mf-samples](https://github.com/3MFConsortium/3mf-samples/tree/master/examples/beam%20lattice)
and renamed to remove spaces. They are redistributed under the
[3MF Consortium sample license](https://github.com/3MFConsortium/3mf-samples/blob/master/LICENSE.md).

| File | Beams | Lattice settings | What it exercises |
| --- | --- | --- | --- |
| `pyramid.3mf` | 391 | `radius=1`, `minlength=0.0001`, `cap=sphere` | Lattice-only object with no triangles, per-beam `r1`, and conical beams with distinct `r1`/`r2` |
| `variable_voronoi.3mf` | 1291 | `radius=0.5`, `minlength=0.005`, `clipping=inside`, `clippingmesh=1` | Clipping a lattice against a separate 100 mm cube object, and beams that inherit the lattice radius |
| `spinal_implant.3mf` | 11821 | `radius=0.25`, `minlength=0.000506664`, `cap=sphere` | A large lattice built alongside a separate solid mesh object in the same build |

These are used by `examples/lattices/beam_lattice/` and by the
`docs/source/guides/3mf-beam-lattice.md` guide.
