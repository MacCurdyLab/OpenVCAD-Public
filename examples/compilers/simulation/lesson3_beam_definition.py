"""
Shared Lesson 3 beam definition for the simulation compiler guide.
"""
import pyvcad as pv

BAR_LENGTH = 60.0
BAR_WIDTH = 12.0
BAR_HEIGHT = 12.0
HALF_LENGTH = 0.5 * BAR_LENGTH
ROOT_MODULUS = 2400.0
TIP_MODULUS = 400.0
POISSONS_RATIO = 0.28


def build_design():
    beam = pv.RectPrism(pv.Vec3(0, 0, 0), pv.Vec3(BAR_LENGTH, BAR_WIDTH, BAR_HEIGHT))
    beam.set_attribute(
        pv.DefaultAttributes.MODULUS,
        pv.FloatAttribute(
            f"{ROOT_MODULUS} - {ROOT_MODULUS - TIP_MODULUS} * clamp((x + {HALF_LENGTH}) / {BAR_LENGTH}, 0, 1)"
        )
    )
    beam.set_attribute(
        pv.DefaultAttributes.POISSONS_RATIO,
        pv.FloatAttribute(f"{POISSONS_RATIO}")
    )
    return beam
