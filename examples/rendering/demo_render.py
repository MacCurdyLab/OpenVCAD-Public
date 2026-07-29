import pyvcad as pv
from pyvcad_rendering import Render

def build_demo_scene():
    materials = pv.default_materials

    modulus_attr = pv.FloatAttribute("x/50 + 1")
    tough_attr = pv.FloatAttribute("-x/50+2")

    rect_prism = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(100,10,3))
    rect_prism.set_attribute(pv.DefaultAttributes.MODULUS,modulus_attr)
    rect_prism.set_attribute(pv.DefaultAttributes.TOUGHNESS,tough_attr)

    return rect_prism, materials


def main() -> int:
    scene, materials = build_demo_scene()
    Render(scene, materials)


if __name__ == "__main__":
    raise SystemExit(main())
