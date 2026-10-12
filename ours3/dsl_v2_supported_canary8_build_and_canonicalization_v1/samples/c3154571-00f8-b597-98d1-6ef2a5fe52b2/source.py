import cadquery as cq

outer_radius = 30.0
inner_cavity_radius = 10.0
block_height = 40.0
fillet_radius = 1.0
countersink_dia = 12.0
countersink_depth = 2.0
hole_dia = 6.0
num_holes = 4
hole_center_offset = outer_radius - 5.0
groove_radius = inner_cavity_radius + 2.0
groove_height = 5.0
groove_start_z = block_height - groove_height - 5.0
tab_thickness = 5.0
tab_height = 8.0
boss_radius = 4.0
boss_height = 10.0

tab_start_y = (block_height - tab_height) / 2.0
profile_points = [
    (0, 0),
    (outer_radius, 0),
    (outer_radius, tab_start_y),
    (outer_radius + tab_thickness, tab_start_y),
    (outer_radius + tab_thickness, tab_start_y + tab_height),
    (outer_radius, tab_start_y + tab_height),
    (outer_radius, block_height),
    (0, block_height),
]

base = (
    cq.Workplane("XZ")
    .polyline(profile_points)
    .close()
    .revolve()
)
base = base.edges("%CIRCLE and >Z").fillet(fillet_radius)

cavity = cq.Workplane("XY").circle(inner_cavity_radius).extrude(block_height + 1)
result = base.cut(cavity)

groove = (
    cq.Workplane("XY")
    .circle(groove_radius)
    .extrude(groove_height)
    .translate((0, 0, groove_start_z))
)
result = result.cut(groove)

boss = (
    cq.Workplane("XY")
    .center(outer_radius, 0)
    .circle(boss_radius)
    .extrude(boss_height)
)
result = result.union(boss)

cutter_cyl = cq.Workplane("XY").circle(hole_dia / 2).extrude(block_height + 1)
counter = (
    cq.Solid.makeCone(countersink_depth, countersink_dia / 2, hole_dia / 2)
    .translate((0, 0, block_height - countersink_depth))
)
hole_cutter = cutter_cyl.union(counter)

for i in range(num_holes):
    angle = i * 360.0 / num_holes
    rotated = hole_cutter.rotate((0, 0, 0), (0, 0, 1), angle).translate((hole_center_offset, 0, 0))
    result = result.cut(rotated)

