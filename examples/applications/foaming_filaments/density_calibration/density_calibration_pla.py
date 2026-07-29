import pyvcad as pv
import pyvcad_rendering as viz
import pyvcad_compilers as pvc
import pyvcad_attribute_resolver as resolver

resolver.register_foaming_conversions()

sample_size = pv.Vec3(30,30,7)
separation_x = 3
separation_y = 3

def make_sample(x_index, y_index, temperature):
    temperature_attr = pv.FloatAttribute(temperature)
    sample = pv.RectPrism(pv.Vec3(x_index*(sample_size.x+separation_x), y_index*(sample_size.y+separation_y), 0), sample_size)
    sample.set_attribute(pv.DefaultAttributes.TEMPERATURE, temperature_attr)
    return sample


bbox_union = pv.BBoxUnion()
bbox_union.add_child(make_sample(0,0,216))
bbox_union.add_child(make_sample(1,0,220))
bbox_union.add_child(make_sample(2,0,224))
bbox_union.add_child(make_sample(3,0,228))
bbox_union.add_child(make_sample(4,0,232))
bbox_union.add_child(make_sample(5,0,236))
bbox_union.add_child(make_sample(6,0,240))
bbox_union.add_child(make_sample(7,0,244))
bbox_union.add_child(make_sample(8,0,248))
bbox_union.add_child(make_sample(9,0,252))
bbox_union.add_child(make_sample(9,1,256))
bbox_union.add_child(make_sample(9,2,260))
bbox_union.add_child(make_sample(9,3,264))

root = resolver.adapt(bbox_union, ["flow_rate"], tags=["foaming_pla"])

viz.Render(root)

printer_profile_path = "../profiles/prusa_xl_multitool.ini"
filament_profile_path = "../profiles/ColorFabb_LW_PLA.ini"
regions = 13

compiler = pvc.PrusaSlicerProjectCompiler(root, pv.Vec3(0.25,0.25,0.25),
                                     "density_calibration_pla.3mf",
                                     regions,
                                     printer_profile_path, filament_profile_path)
compiler.compile()
