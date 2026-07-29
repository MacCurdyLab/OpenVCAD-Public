import os
import pyvcad as pv
from pyvcad_rendering import Render_Turntable_Animation

if __name__ == "__main__":
    # Create simple geometry (Two offset spheres)
    s1 = pv.Sphere(pv.Vec3(0, 0, 0), 4)
    s2 = pv.Sphere(pv.Vec3(4, 0, 0), 4) # slightly smaller, offset
    
    obj = pv.Union(s1, s2)
    materials = pv.default_materials
    
    out_dir = os.path.join(os.path.dirname(__file__), "turntable_frames")
    
    # Custom settings to make it look nice
    settings = {
        "quality": "medium",
        "render_mode": "iso_surface",
        "visualized_attribute": "none",               # Replace "none" with attribute name if available
        "scale_bar_palette": "auto",                  # Auto per-attribute, or override: viridis/plasma/inferno/magma/cividis/turbo/grayscale
        "show_bbox": False,
        "show_origin": False,
        "show_orientation_marker": True,              # Show the top-right axis widget
        "background_color": (1.0, 1.0, 1.0),          # White background
        "transparent_background": True,               # Set True for transparent output
        "scale_bar_visible": False,                   # Force legend on/off independent of default behavior
        "scale_bar_show_annotations": True,           # Hide legend title/ticks if False
        "scalar_range_mode": "auto",                  # "auto" or "fixed"
        "scalar_range_min": None,
        "scalar_range_max": None,
        "camera_state": None                          # Serialized camera dict copied from the GUI Camera dialog
    }
    
    print(f"Rendering turntable animation to {out_dir} ...")
    
    # Render a 3-second GIF at 30fps (auto-calculates 90 frames)
    Render_Turntable_Animation(
        vcad_object=obj, 
        materials=materials, 
        output_dir=out_dir, 
        duration=3.0,                # Total animation length in seconds
        fps=30,                      # Frames per second (default)
        distance_multiplier=2.0, 
        elevation_angle_deg=25.0, 
        settings=settings,
        output_format="all",         # Options: "gif", "webp", "mp4", "webm", "all"
        keep_frames=False            # Set True to keep the intermediate PNG files
    )
    
    print("Animation rendering complete!")
