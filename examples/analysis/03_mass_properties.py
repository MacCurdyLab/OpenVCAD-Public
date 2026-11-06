"""Volume, mass, centre of mass and inertia of a two-material mallet."""

import pyvcad as pv
import pyvcad_rendering as viz

# The J750 configuration lists each material's published density in g/cm^3.
materials = pv.j750_materials

# A rigid head across the top of a rubber-like handle.
head = pv.Rotate(0.0, 90.0, 0.0, pv.Cylinder(pv.Vec3(0.0, 0.0, 0.0), 12.0, 50.0))
head.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,
                   pv.VolumeFractionsAttribute([(1.0, materials.id("VeroCyan"))]))
handle = pv.Cylinder(pv.Vec3(0.0, 0.0, -60.0), 6.0, 100.0)
handle.set_attribute(pv.DefaultAttributes.VOLUME_FRACTIONS,
                     pv.VolumeFractionsAttribute([(1.0, materials.id("Agilus30Mgn"))]))
mallet = pv.Union(head, handle)

# Mass comes from the volume fractions times each material's density. A design that is
# only geometry would pass density=... instead; a modelled "density" attribute wins.
report = pv.mass_properties(mallet, 0.5, materials=materials)

print(f"volume          {report.volume:10.1f} mm^3  (+/- {report.volume_error:.1f})")
print(f"surface area    {report.surface_area:10.1f} mm^2  (+/- {report.surface_area_error:.1f})")
print(f"mass            {report.mass:10.2f} g     from {report.mass_source.name}")
print(f"centre of mass  {report.center_of_mass.round(2)} mm")
print(f"principal moments {report.principal_moments.round(1)} g mm^2")
for material, volume in report.material_volumes.items():
    print(f"  {materials.name(material):12s} {volume:10.1f} mm^3")

# In the viewer, Inspect > Mass Properties shows these numbers and draws the centre of mass.
viz.Render(mallet, materials)
