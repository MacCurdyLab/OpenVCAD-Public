import pyvcad as pv

materials = pv.default_materials()

bar = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(100,50,10), materials.id("gray"))

def func_a(x, y, z, rho, phic, r, theta, phis):
    return x/100 + 0.5

def func_b(x, y, z, rho, phic, r, theta, phis):
    return -x/100 + 0.5

# A functional gradient that is 100% blue at x=-50 and 100% at x=50
root = pv.FGrade([func_a, func_b],
                 [materials.id("red"), materials.id("blue")], False)
root.set_child(bar)