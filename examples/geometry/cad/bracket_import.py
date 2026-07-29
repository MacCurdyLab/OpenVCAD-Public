"""Import the bundled bracket from either a STEP or IGES file."""

from pathlib import Path

import pyvcad as pv
import pyvcad_rendering as viz

# Choose either "step" or "iges". Both files describe the same closed bracket.
cad_format = "step"

model_files = {
    "step": "bracket.step",
    "iges": "bracket.iges",
}
if cad_format not in model_files:
    raise ValueError("cad_format must be 'step' or 'iges'")

model_path = Path(__file__).resolve().parents[2] / "data" / "3d_models" / model_files[cad_format]

# Fast mode discretizes the CAD solid during prepare(). Use exact mode when
# accuracy is more important than sampling speed.
root = pv.CAD(str(model_path), use_fast_mode=True)
modulus_min = 900.0
modulus_max = 2600.0
gradient_height = 32.0
root.set_attribute(
    pv.DefaultAttributes.MODULUS,
    pv.FloatAttribute(
        f"{modulus_min} + ({modulus_max} - {modulus_min}) "
        f"* clamp(z / {gradient_height}, 0, 1)"
    ),
)

viz.Render(root)
