import cadquery as cq

# Parameters
outer_radius = 30.0
wall_thickness = 2.0
base_thickness = 5.0
total_height = 20.0
hole_radius = 5.0
hole_stop = 3.0
rib_thickness = 0.8
rib_spacing = 8.0
fillet_radius = 0.2

inner_radius = outer_radius - wall_thickness
interior_height = total_height - base_thickness
interior_start_z = base_thickness

# Outer solid
outer = cq.Workplane("XY").circle(outer_radius).extrude(total_height)
inner_cyl = cq.Workplane("XY").circle(inner_radius).extrude(total_height)
shell = outer.cut(inner_cyl)
hole = cq.Workplane("XY").circle(hole_radius).extrude(total_height - hole_stop)
shell = shell.cut(hole)
# Rib lattice with filleted vertical edges
rib_union = cq.Workplane("XY")
# X ribs
x_pos = -inner_radius + rib_spacing
while x_pos < inner_radius:
    rib = (
        cq.Workplane("XY")
        .box(rib_thickness, 2*inner_radius, interior_height)
        .translate((x_pos, 0, interior_start_z + interior_height/2))
        .edges("|Z")
        .fillet(fillet_radius)
    )
    rib_union = rib_union.union(rib)
    x_pos += rib_spacing
# Y ribs
y_pos = -inner_radius + rib_spacing
while y_pos < inner_radius:
    rib = (
        cq.Workplane("XY")
        .box(2*inner_radius, rib_thickness, interior_height)
        .translate((0, y_pos, interior_start_z + interior_height/2))
        .edges("|Z")
        .fillet(fillet_radius)
    )
    rib_union = rib_union.union(rib)
    y_pos += rib_spacing
ribs = rib_union.intersect(inner_cyl)
result = shell.union(ribs)
