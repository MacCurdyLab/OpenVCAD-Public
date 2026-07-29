import os
import pyvcad as pv
from pyvcad_rendering import Render_Image

if __name__ == "__main__":
    # Create simple geometry: a sphere
    obj = pv.Sphere(pv.Vec3(0, 0, 0), 5.0)
    
    # Create an internal gradient (e.g. temperature hot in center)
    attr = pv.FloatAttribute("100 * (1 - sqrt(x*x + y*y + z*z)/5)")
    obj.set_attribute(pv.DefaultAttributes.TEMPERATURE, attr)
    out_path = os.path.join(os.path.dirname(__file__), "test_headless_clipping.png")
    
    # Full list of settings with clipping plane enabled
    settings = {
        "quality": "medium",                 # Options: low, medium, high, ultra
        "render_mode": "iso_surface",        # Options: iso_surface, volumetric
        "visualized_attribute": pv.DefaultAttributes.TEMPERATURE, 
        "scale_bar_palette": "auto",         # Auto per-attribute, or override: viridis/plasma/inferno/magma/cividis/turbo/grayscale
        
        # --- Clipping Plane Settings ---
        "clipping_plane": True,              # Enable clipping plane
        "clipping_plane_origin": (0.0, 0.0, 0.0), # (X, Y, Z) point lying on the plane
        "clipping_plane_normal": (1.0, 0.0, 0.0), # Normal vector pointing *away* from kept region
        # -------------------------------
        
        "use_blending": True,                # Toggle volume blending
        "use_vol_shading": False,            # Volumetric shading (if render_mode is volumetric)
        "show_bbox": False,                  # Show bounding box
        "show_origin": False,                # Show origin axes
        "show_orientation_marker": False,    # Still image output always hides the axis widget
        "background_color": (0.177, 0.177, 0.177), # Background color RGB (dark mode by default)
        "transparent_background": False,
        "scale_bar_visible": True,           # Force legend on/off independent of default behavior
        "scale_bar_show_annotations": True,  # Hide legend title/ticks if False
        "scalar_range_mode": "auto",         # "auto" or "fixed"
        "scalar_range_min": None,
        "scalar_range_max": None,
        
        # Camera Settings (defaults to automatic reset if camera_state and camera_position are None)
        "camera_state": None,                # Serialized camera dict copied from the GUI Camera dialog
        "camera_position": None,             # e.g., (20, 20, 20)
        "camera_focal_point": None,          # e.g., (0, 0, 0)
        "camera_view_up": None,              # e.g., (0, 0, 1)
    }
    
    print(f"Rendering to {out_path}...")
    Render_Image(obj, out_path, settings=settings)
    print("Done!")
