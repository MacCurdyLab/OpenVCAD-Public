import os
import shutil
import random
import math

from PIL import Image, ImageDraw

import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_compilers as pvc

# --- Global Configuration ---
render = True
export = False

sizes = [26, 40, 55, 60] # N x N size in mm
depth_mm = 3.0

DPI = 600          
MIN_FEATURE_RATIO = 0.35    


def generate_macro_fiducial(
    filename="generated_fiducial.png", 
    total_size_mm=50.0, 
    padding_mm=5.0, 
    dpi=600, 
    min_feature_ratio=0.35
):
    """
    Generates a high-contrast B&W ARKit fiducial using only chunky, regular polygons.
    Eliminates all acute angles and thin slivers to ensure robust PolyJet/Inkjet printing.
    """
    # --- 1. Dimension & Canvas Setup ---
    total_pixels = int((total_size_mm / 25.4) * dpi)
    padding_pixels = int((padding_mm / 25.4) * dpi)
    
    active_pixels = total_pixels - (2 * padding_pixels)
    offset = padding_pixels
    
    if active_pixels <= 0:
        raise ValueError("Padding is too large! Active tracking area must be > 0.")
        
    min_radius_px = int(active_pixels * min_feature_ratio)
    
    # Mode "1" guarantees 1-bit strict B&W. Canvas is white.
    img = Image.new("1", (total_pixels, total_pixels), 1)
    draw = ImageDraw.Draw(img)
    
    # --- LAYER 1: Chunky Regular Polygons (Drawn First) ---
    num_bold_features = 8 
    
    for i in range(num_bold_features):
        current_color = 0 if i % 2 == 0 else 1
            
        max_radius_px = int(active_pixels * 0.45)
        shape_radius = min_radius_px if min_radius_px >= max_radius_px else random.randint(min_radius_px, max_radius_px)
        
        # Constrain the center point so the entire radius fits inside the active area.
        # This prevents the shapes from being "squished" against the border into thin lines.
        cx_min = offset + shape_radius
        cx_max = offset + active_pixels - shape_radius
        
        # Fallback if the requested radius is highly constrained
        if cx_min >= cx_max:
            cx, cy = offset + active_pixels//2, offset + active_pixels//2
        else:
            cx = random.randint(cx_min, cx_max)
            cy = random.randint(cx_min, cx_max)
            
        # Select from 4, 5, 6, or 8 sides. 
        # Banning 3-sided triangles completely eliminates acute internal angles.
        n_sides = random.choice([4, 5, 6, 8])
        rotation_rad = random.uniform(0, 2 * math.pi)
        
        points = []
        for j in range(n_sides):
            angle = rotation_rad + j * (2 * math.pi / n_sides)
            px = cx + shape_radius * math.cos(angle)
            py = cy + shape_radius * math.sin(angle)
            points.append((px, py))
            
        draw.polygon(points, fill=current_color)
        
    # --- LAYER 2: Robust Large Anchors (Drawn Last) ---
    anchor_size = int(active_pixels * 0.35)
    clearance = int(min_radius_px * 0.4) 
    
    top_left_x = offset
    top_left_y = offset
    top_right_x = offset + active_pixels
    bottom_right_y = offset + active_pixels
    
    # 1. Top-Left: Massive Black Square
    draw.rectangle([top_left_x, top_left_y, 
                    top_left_x + anchor_size + clearance, top_left_y + anchor_size + clearance], fill=1)
    draw.rectangle([top_left_x, top_left_y, 
                    top_left_x + anchor_size, top_left_y + anchor_size], fill=0)
    
    # 2. Top-Right: Thick Black Cross
    draw.rectangle([top_right_x - anchor_size - clearance, top_left_y, 
                    top_right_x, top_left_y + anchor_size + clearance], fill=1)
    
    cross_thickness = anchor_size // 2.5
    center_x = top_right_x - (anchor_size // 2)
    center_y = top_left_y + (anchor_size // 2)
    
    draw.rectangle([center_x - cross_thickness//2, top_left_y, 
                    center_x + cross_thickness//2, top_left_y + anchor_size], fill=0)
    draw.rectangle([top_right_x - anchor_size, center_y - cross_thickness//2, 
                    top_right_x, center_y + cross_thickness//2], fill=0)

    # 3. Bottom-Right: Massive Black Circle
    draw.rectangle([top_right_x - anchor_size - clearance, bottom_right_y - anchor_size - clearance, 
                    top_right_x, bottom_right_y], fill=1)
    draw.ellipse([top_right_x - anchor_size, bottom_right_y - anchor_size, 
                  top_right_x, bottom_right_y], fill=0)

    # --- Save Output ---
    try:
        img.save(filename, dpi=(dpi, dpi))
        print(f"SUCCESS: Generated {filename} ({total_size_mm}mm)")
    except Exception as e:
        print(f"ERROR saving {filename}: {e}")


# --- PyVCAD Integration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_fiducial(size):
    padding = size * 0.05

    filename = "generated_fiducial_{}mm.png".format(size)
    generate_macro_fiducial(
        filename=filename, 
        total_size_mm=size,
        padding_mm=padding,
        dpi=DPI,
        min_feature_ratio=MIN_FEATURE_RATIO
    )

    IMAGE_PATH = os.path.join(SCRIPT_DIR, filename)
    img = Image.open(IMAGE_PATH)
    width, height = img.size
    # Mapping exact mm sizes directly into the voxel size configuration
    image_voxel_size = pv.Vec3(size / width, size / height, depth_mm / height)

    png_loader = pv.PNGLoader.FromImage(
        IMAGE_PATH,
        image_voxel_size,
        depth_mm,
        pv.PNGColorMode.COLOR_RGBA,
        center=True,
    )
    color_volume = png_loader.as_rgba_volume()

    carrier_min, carrier_max = color_volume.bounding_box()
    carrier = pv.RectPrism.FromMinAndMax(carrier_min, carrier_max)
    carrier.set_attribute(pv.DefaultAttributes.COLOR_RGBA, pv.Vec4Attribute(color_volume))
    return carrier

union = pv.BBoxUnion()
previous_translate = 0
for size in sizes:
    fiducial = generate_fiducial(size)
    fiducial = pv.Translate(previous_translate + size/2, 0, 0, fiducial)
    previous_translate += size
    union.add_child(fiducial)
root = union

if render:
    viz.Render(root)

if export:
    def report_progress(label):
        def _report(progress):
            print("{} progress: {:.1f}%".format(label, 100.0 * progress))
        return _report

    _here = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(_here, "output")
    inkjet_output_dir = os.path.join(output_dir, "maclab_logo_inkjet")
    inkjet_prefix = "slice_"
    inkjet_voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
    
    if os.path.isdir(inkjet_output_dir):
        shutil.rmtree(inkjet_output_dir)
    os.makedirs(inkjet_output_dir, exist_ok=True)

    icc_profiles_dir = os.path.join(
        os.path.dirname(os.path.abspath(pvc.__file__)),
        "icc_profiles",
    )
    if not os.path.isdir(icc_profiles_dir):
        icc_profiles_dir = os.path.abspath(
            os.path.join(
                _here,
                "..",
                "..",
                "..",
                "..",
                "compilers",
                "icc_profiles",
            )
        )
    pvc.ColorPipeline.set_icc_resource_path(icc_profiles_dir)

    inkjet_compiler = pvc.ColorInkjetCompiler(
        root,
        inkjet_voxel_size,
        inkjet_output_dir,
        inkjet_prefix,
        "default",
    )
    inkjet_compiler.set_progress_callback(report_progress("ColorInkjet"))
    inkjet_compiler.compile()
    print("Wrote", inkjet_output_dir)