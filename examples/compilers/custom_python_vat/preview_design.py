"""Open the example exposure-gradient design in the interactive renderer."""

import pyvcad_rendering as viz

from design import build_design


root = build_design()
viz.Render(root)
