import os
import pyvcad as pv
from pyvcad_rendering import Render_Image

if __name__ == "__main__":
    # Create simple geometry: a sphere
    obj = pv.Sphere(pv.Vec3(0, 0, 0), 5.0)
    out_path = os.path.join(os.path.dirname(__file__), "test_headless_sdf.png")
    
    # Full list of settings with clipping plane enabled to see the internal SDF gradient
    settings = {
        "quality": "medium",
        "render_mode": "iso_surface",
        "visualized_attribute": "Signed Distance", 
        "scale_bar_palette": "auto",         # Auto per-attribute, or override: viridis/plasma/inferno/magma/cividis/turbo/grayscale
        
        # --- Clipping Plane Settings ---
        "clipping_plane": True,
        "clipping_plane_origin": (0.0, 0.0, 0.0),
        "clipping_plane_normal": (1.0, 0.0, 0.0),
        
        "use_blending": True,
        "show_bbox": False,
        "show_origin": False,
        "background_color": (0.177, 0.177, 0.177),
    }
    
    print(f"Rendering to {out_path}...")
    Render_Image(obj, out_path, settings=settings)
    print("Done!")
