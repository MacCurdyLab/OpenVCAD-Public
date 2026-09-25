"""Example design for the custom Python grayscale VAT compiler."""

import pyvcad as pv


EXPOSURE = "exposure"


def build_design():
    length_mm = 30.0
    width_mm = 16.0
    height_mm = 6.0

    prism = pv.RectPrism(
        pv.Vec3(0, 0, 0),
        pv.Vec3(length_mm, width_mm, height_mm),
    )

    # x runs from -15 mm to +15 mm. This expression maps that span
    # linearly from exposure 0.1 to exposure 1.0.
    exposure_gradient = pv.FloatAttribute("0.03 * x + 0.55")
    prism.set_attribute(EXPOSURE, exposure_gradient)

    return prism
