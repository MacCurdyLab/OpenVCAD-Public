"""A small, reusable grayscale VAT compiler written entirely in Python."""

import math
from pathlib import Path

import numpy as np
from PIL import Image
import pyvcad as pv


class GrayscaleVatCompiler:
    """Compile an OpenVCAD design into full-bed 8-bit grayscale PNG layers."""

    exposure_attribute = "exposure"

    def __init__(
        self,
        root,
        printer_size_mm,
        dpi,
        layer_height_mm,
        output_directory,
    ):
        self.root = root
        self.printer_size_mm = printer_size_mm
        self.dpi = float(dpi)
        self.layer_height_mm = float(layer_height_mm)
        self.output_directory = Path(output_directory)
        self.undefined_sample_count = 0

        self._validate_settings()
        self.pixel_pitch_mm = 25.4 / self.dpi
        self.image_width = max(
            1, round(self.printer_size_mm.x / self.pixel_pitch_mm)
        )
        self.image_height = max(
            1, round(self.printer_size_mm.y / self.pixel_pitch_mm)
        )

    def _validate_settings(self):
        printer_dimensions = (
            self.printer_size_mm.x,
            self.printer_size_mm.y,
            self.printer_size_mm.z,
        )
        if any(value <= 0 for value in printer_dimensions):
            raise ValueError("Printer dimensions must be positive.")
        if self.dpi <= 0:
            raise ValueError("Printer DPI must be positive.")
        if self.layer_height_mm <= 0:
            raise ValueError("Layer height must be positive.")

    def _prepare_placement(self):
        object_min, object_max = self.root.bounding_box()
        object_size = (
            object_max.x - object_min.x,
            object_max.y - object_min.y,
            object_max.z - object_min.z,
        )
        printer_size = (
            self.printer_size_mm.x,
            self.printer_size_mm.y,
            self.printer_size_mm.z,
        )

        dimension_names = ("X", "Y", "Z")
        for name, object_length, printer_length in zip(
            dimension_names, object_size, printer_size
        ):
            if object_length > printer_length:
                raise RuntimeError(
                    "The object is {:.3f} mm in {}, but the printer allows "
                    "only {:.3f} mm.".format(object_length, name, printer_length)
                )

        self.object_min = object_min
        self.object_max = object_max
        self.object_size = object_size
        self.object_center_x = (object_min.x + object_max.x) / 2.0
        self.object_center_y = (object_min.y + object_max.y) / 2.0
        self.layer_count = max(1, math.ceil(object_size[2] / self.layer_height_mm))

    def _points_for_layer(self, layer_index):
        world_z = (
            self.object_min.z
            + (layer_index + 0.5) * self.layer_height_mm
        )
        points = []

        for y_index in range(self.image_height):
            bed_y = (y_index + 0.5) * self.pixel_pitch_mm
            world_y = (
                self.object_center_y
                + bed_y
                - self.printer_size_mm.y / 2.0
            )

            for x_index in range(self.image_width):
                bed_x = (x_index + 0.5) * self.pixel_pitch_mm
                world_x = (
                    self.object_center_x
                    + bed_x
                    - self.printer_size_mm.x / 2.0
                )
                points.append(pv.Vec3(world_x, world_y, world_z))

        return points

    def _grayscale_layer(self, points, samples):
        layer = np.zeros(
            (self.image_height, self.image_width),
            dtype=np.uint8,
        )

        for index, (signed_distance, attributes) in enumerate(samples):
            if signed_distance is None or signed_distance > 0:
                continue

            if (
                attributes is None
                or not attributes.has_sample(self.exposure_attribute)
            ):
                self.undefined_sample_count += 1
                continue

            exposure = attributes.get_sample(self.exposure_attribute)
            if not isinstance(exposure, (int, float)):
                raise RuntimeError(
                    "'{}' must be a floating-point attribute.".format(
                        self.exposure_attribute
                    )
                )
            if not math.isfinite(exposure) or exposure < 0.0 or exposure > 1.0:
                point = points[index]
                raise RuntimeError(
                    "Exposure must be between 0 and 1; sampled {} at "
                    "({:.3f}, {:.3f}, {:.3f}) mm.".format(
                        exposure,
                        point.x,
                        point.y,
                        point.z,
                    )
                )

            y_index = index // self.image_width
            x_index = index % self.image_width
            layer[y_index, x_index] = round(exposure * 255.0)

        return layer

    def compile(self, progress_callback=None):
        """Compile the design and return the paths of the generated PNG files."""

        if self.exposure_attribute not in self.root.attribute_list():
            raise RuntimeError(
                "The design does not contain an '{}' attribute.".format(
                    self.exposure_attribute
                )
            )

        self._prepare_placement()
        self.output_directory.mkdir(parents=True, exist_ok=True)
        for old_layer in self.output_directory.glob("layer_*.png"):
            old_layer.unlink()

        voxel_size = pv.Vec3(
            self.pixel_pitch_mm,
            self.pixel_pitch_mm,
            self.layer_height_mm,
        )

        # TreeSampler prepares the root with this voxel size and a narrow-band
        # width of six times the largest voxel dimension.
        sampler = pv.TreeSampler(self.root, voxel_size)
        output_paths = []
        self.undefined_sample_count = 0
        last_progress = -1

        def report_progress(layer_index, sample_progress):
            nonlocal last_progress
            overall = round(
                100.0
                * (layer_index + sample_progress / 100.0)
                / self.layer_count
            )
            if progress_callback is not None and overall > last_progress:
                last_progress = overall
                progress_callback(overall)

        for layer_index in range(self.layer_count):
            points = self._points_for_layer(layer_index)
            samples = sampler.sample_points(
                points,
                lambda percent: report_progress(layer_index, percent),
            )
            layer = self._grayscale_layer(points, samples)

            # PNG rows are stored top-to-bottom. Flipping here makes the
            # displayed lower-left pixel correspond to the print-bed origin.
            output_path = self.output_directory / "layer_{:04d}.png".format(
                layer_index
            )
            Image.fromarray(np.flipud(layer)).save(output_path)
            output_paths.append(output_path)

        if self.undefined_sample_count:
            print(
                "Warning: {} inside samples had no '{}' value and were "
                "written as exposure 0.".format(
                    self.undefined_sample_count,
                    self.exposure_attribute,
                )
            )

        return output_paths
