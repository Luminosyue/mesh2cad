import cadquery as cq

# Parameters
length = 80.0
outer_radius = 15.0
outer_wall_thickness = 3.0
inner_wall_outer_radius = 9.0
inner_wall_thickness = 2.0
chamfer_distance = 0.5
slot_width = 2.0
slot_height = 4.0
slot_count = 24
slot_depth_extra = 0.5

groove_width = 5.0
groove_depth = 1.5
groove_length = length - 10.0
rib_thickness = 5.0
rib_positions = [length * 0.25, length * 0.5, length * 0.75]

# Outer wall creation
outer_cyl = cq.Workplane('XY').circle(outer_radius).extrude(length)
outer_hole = cq.Workplane('XY').circle(outer_radius - outer_wall_thickness).extrude(length)
outer_wall = outer_cyl.cut(outer_hole)

# Inner wall creation
inner_outer_cyl = cq.Workplane('XY').circle(inner_wall_outer_radius).extrude(length)
inner_inner_cyl = cq.Workplane('XY').circle(inner_wall_outer_radius - inner_wall_thickness).extrude(length)
inner_wall = inner_outer_cyl.cut(inner_inner_cyl)

# Ribs connecting walls
rib_outer_radius = outer_radius - outer_wall_thickness
rib_inner_radius = inner_wall_outer_radius
rib_base = (cq.Workplane('XY')
            .circle(rib_outer_radius)
            .circle(rib_inner_radius)
            .extrude(rib_thickness))
rib_union = cq.Workplane('XY')
for z in rib_positions:
    rib_union = rib_union.union(rib_base.translate((0, 0, z - rib_thickness / 2)))

# Combine walls and ribs into a single solid
result = outer_wall.union(inner_wall).union(rib_union)

# Cable groove (cut into inner wall cavity)
# Position the groove block radially inside the inner cavity
groove_center_radius = inner_wall_outer_radius - inner_wall_thickness / 2.0
groove_offset = groove_center_radius - groove_depth / 2.0
groove_block = (cq.Workplane('XY')
                .box(groove_depth, groove_width, groove_length)
                .translate((groove_offset, 0, 0)))
result = result.cut(groove_block)

# Vent slots pattern on outer wall outer surface
slot_cut = (cq.Workplane()
            .faces('|Z')
            .workplane()
            .center(outer_radius - outer_wall_thickness / 2.0, 0)
            .polarArray(count=slot_count, startAngle=0, angle=360, radius=outer_radius - outer_wall_thickness / 2.0)
            .rect(slot_width, slot_height)
            .extrude(outer_wall_thickness + slot_depth_extra))
result = result.cut(slot_cut)

# Chamfer outer edges for safety
result = result.edges('|Z').chamfer(chamfer_distance)
