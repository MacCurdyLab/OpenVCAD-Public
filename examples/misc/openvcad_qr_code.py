import os

import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

# Material names can be swapped for any names present in pv.default_materials.
yellow_material_name = "yellow"
magenta_material_name = "magenta"
clear_material_name = "clear"
black_material_name = "black"

# Shared paths and mesh loading controls.
data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "3d_models")
qr_base_file = "qr_code_base.3mf"
qr_code_file = "qr_code_code.3mf"
qr_border_file = "qr_code_border.3mf"
mesh_center = False
mesh_disable_validation = True

# Bar controls.
bar_center = pv.Vec3(0, 0, 0)
bar_size = pv.Vec3(173, 32, 12)

# QR controls. The source QR meshes are already centered around the origin.
qr_scale = 1.0
qr_translation = pv.Vec3(-69, 0, -1.5)

# Text controls. These defaults match the old STL text footprint inside the bar.
text_string = "OpenVCAD"
text_height = 26.5
text_depth = 5.6
text_font = "Arial"
text_aspect = pv.FontAspect.Regular
text_horizontal_alignment = pv.HorizontalAlignment.Center
text_vertical_alignment = pv.VerticalAlignment.Center
text_scale = 1.0
text_rotation_pitch = 0
text_rotation_yaw = 0
text_rotation_roll = 180
text_translation = pv.Vec3(14.5, -1.75, 0)

# Text material controls.
text_gradient_width = 136

# Gyroid controls. Disable use_gyroid_fill to render the solid Text geometry.
use_gyroid_fill = True
gyroid_frequency_scale = 1.1
gyroid_period = 1.0
gyroid_offset = 0.5
gyroid_min = pv.Vec3(-72, -18, -6)
gyroid_max = pv.Vec3(72, 18, 6)


def material_id(material_name):
    return materials.id(material_name)


def data_path(filename):
    return os.path.join(data_dir, filename)


def solid_volume_fractions(material):
    return pv.VolumeFractionsAttribute([("1.0", material)])


def set_solid_volume_fraction(node, material):
    node.set_attribute(
        pv.DefaultAttributes.VOLUME_FRACTIONS,
        solid_volume_fractions(material)
    )
    return node


def load_qr_mesh(filename, material):
    mesh = pv.Mesh(
        data_path(filename),
        mesh_center,
        mesh_disable_validation
    )
    return set_solid_volume_fraction(mesh, material)


yellow = material_id(yellow_material_name)
magenta = material_id(magenta_material_name)
clear = material_id(clear_material_name)
black = material_id(black_material_name)

# Build the QR code from the existing 3MF components.
qr_base = load_qr_mesh(qr_base_file, yellow)
qr_code = load_qr_mesh(qr_code_file, black)
qr_border = load_qr_mesh(qr_border_file, black)
qr_code_combined = pv.Union(0.0, [qr_base, qr_code, qr_border])
qr_code_combined = pv.Scale(qr_scale, qr_code_combined)
qr_code_combined = pv.Translate(qr_translation.x, qr_translation.y, qr_translation.z, qr_code_combined)

# Build the OpenVCAD text directly with the Text node and apply a yellow/magenta gradient.
openvcad_text = pv.Text(
    text_string,
    text_height,
    text_depth,
    text_aspect,
    text_font,
    text_horizontal_alignment,
    text_vertical_alignment
)
openvcad_text.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute([
        (f"x/{text_gradient_width} + 0.5", magenta),
        (f"-x/{text_gradient_width} + 0.5", yellow),
    ])
)

if use_gyroid_fill:
    gyroid_expression = (
        f"sin(({gyroid_frequency_scale} * pi * x) / {gyroid_period}) * "
        f"cos(({gyroid_frequency_scale} * pi * y) / {gyroid_period}) + "
        f"sin(({gyroid_frequency_scale} * pi * y) / {gyroid_period}) * "
        f"cos(({gyroid_frequency_scale} * pi * z) / {gyroid_period}) + "
        f"sin(({gyroid_frequency_scale} * pi * z) / {gyroid_period}) * "
        f"cos(({gyroid_frequency_scale} * pi * x) / {gyroid_period}) + "
        f"{gyroid_offset}"
    )
    gyroid = pv.Function(gyroid_expression, gyroid_min, gyroid_max)
    text_node = pv.Intersection(0.0, [openvcad_text, gyroid])
else:
    text_node = openvcad_text

text_node = pv.Scale(text_scale, text_node)
text_node = pv.Rotate(text_rotation_pitch, text_rotation_yaw, text_rotation_roll, text_node)
text_node = pv.Translate(text_translation.x, text_translation.y, text_translation.z, text_node)

# Create a clear rectangular prism to hold the QR code and text.
bar = pv.RectPrism(bar_center, bar_size)
bar = set_solid_volume_fraction(bar, clear)

# Child order is intentional: feature attributes win over the clear bar in overlaps.
root = pv.Union(0.0, [qr_code_combined, text_node, bar])

viz.Render(root, materials=materials)
