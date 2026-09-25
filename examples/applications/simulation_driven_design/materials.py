"""Settled material endpoints and the illustrative mixture rule for Study 1."""

import numpy as np


AGILUS30_YOUNGS_MODULUS_MPA = 1.265
AGILUS30_POISSONS_RATIO = 0.49
AGILUS30_DENSITY_G_CM3 = 1.145

VERO_YOUNGS_MODULUS_MPA = 2500.0
VERO_POISSONS_RATIO = 0.35
VERO_DENSITY_G_CM3 = 1.18


def illustrative_effective_properties(vero_fraction):
    """Linearly mix endpoints for workflow demonstration, not calibration."""
    fraction = np.clip(np.asarray(vero_fraction, dtype=np.float64), 0.0, 1.0)
    modulus = (
        AGILUS30_YOUNGS_MODULUS_MPA * (1.0 - fraction)
        + VERO_YOUNGS_MODULUS_MPA * fraction
    )
    poissons_ratio = (
        AGILUS30_POISSONS_RATIO * (1.0 - fraction)
        + VERO_POISSONS_RATIO * fraction
    )
    return modulus, poissons_ratio
