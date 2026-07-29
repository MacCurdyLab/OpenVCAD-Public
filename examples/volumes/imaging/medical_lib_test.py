import pyvcad as pv
import pyvcad_medical as med

opacity_function = lambda t: 1.0
demo_map = med.color_maps.create_linear_gradient_hu_map(0,1000,steps=100, opacity_function=opacity_function, palette=med.raw_color_palettes["grayscale"])

med.color_maps.plot_opacity_function(med.color_maps.sigmoid_opacity_base)

med.color_maps.plot_hu_color_map(demo_map, 0, 1000)