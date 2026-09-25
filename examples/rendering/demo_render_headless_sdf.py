# This script demos saving a slice of a model's signed distance field (SDF) to a PNG without opening a window.
# VisualizeSDF samples one principal-plane slice of the field, both inside and outside the object, and draws the
# chosen iso-surface as a contour. The interactive renderer shows the same view from Inspect > SDF Slice Viewer.

import os

import matplotlib
matplotlib.use("Agg")  # Headless backend: build the figure without a display

import pyvcad as pv
from pyvcad_rendering import VisualizeSDF

if __name__ == "__main__":
    # Create simple geometry: a sphere
    obj = pv.Sphere(pv.Vec3(0, 0, 0), 5.0)

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    out_dir = os.path.join(repo_root, ".tmp")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "test_headless_sdf.png")

    # The YZ plane at X=0 cuts the sphere through its center, showing the SDF
    # gradient from the core (negative) through the surface (zero) to the outside (positive).
    fig, ax = VisualizeSDF(obj, offset=0.0, plane="yz", resolution=300, iso_surface=0.0, show=False)

    print(f"Rendering to {out_path}...")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print("Done!")
