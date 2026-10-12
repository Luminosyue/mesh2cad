import cadquery as cq
import math
outer_diameter = 60.0
wall_thickness = 5.0
outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
body_length = 80.0
relief_groove_width = 12.0
relief_groove_depth = 2.0
relief_groove_center = 40.0
top_fillet_radius = 4.0
base_chamfer = 2.0
inlet_diameter = 14.0
outlet_diameter = 10.0
inlet_z = 20.0
outlet_z = 60.0
flange_outer_diameter = 90.0
flange_outer_radius = flange_outer_diameter / 2.0
flange_thickness = 6.0
bolt_hole_diameter = 5.0
bolt_hole_count = 4
bolt_circle_diameter = 50.0
pocket_width = 15.0
pocket_height = 20.0
pocket_depth = 8.0
rib_thickness = 4.0
rib_height = 30.0
# Base body solid
outer_cyl = cq.Workplane('XY').circle(outer_radius).extrude(body_length)
inner_cyl = cq.Workplane('XY').circle(inner_radius).extrude(body_length)
body = outer_cyl.cut(inner_cyl)
# Relief groove
relief_radius = inner_radius - relief_groove_depth
relief_cyl = cq.Workplane('XY').circle(relief_radius).extrude(relief_groove_width)
relief_z = relief_groove_center - relief_groove_width/2.0
body = body.cut(relief_cyl.translate((0,0,relief_z)))
# Top fillet and base chamfer
body = body.edges('>Z').fillet(top_fillet_radius)
body = body.edges('<Z').chamfer(base_chamfer)
# Axial inlet/outlet holes
inlet_cyl = cq.Workplane('XY').circle(inlet_diameter/2.0).extrude(body_length+2).translate((0,0,inlet_z - body_length/2.0))
body = body.cut(inlet_cyl)
outlet_cyl = cq.Workplane('XY').circle(outlet_diameter/2.0).extrude(body_length+2).translate((0,0,outlet_z - body_length/2.0))
body = body.cut(outlet_cyl)
# Flange disc overlapping body by 2 units
flange = cq.Workplane('XY').circle(flange_outer_radius).extrude(flange_thickness)
flange = flange.cut(cq.Workplane('XY').circle(outer_radius).extrude(flange_thickness))
flange = flange.translate((0,0,-flange_thickness+2))
# Merge body and flange
merged = body.union(flange).combine()
# Side rectangular pocket cut
pocket = cq.Workplane('XZ').rect(pocket_width, pocket_height).extrude(pocket_depth).translate((outer_radius-pocket_depth/2.0,0,body_length/2.0))
merged = merged.cut(pocket)
# Add four external ribs intersecting outer wall
for i in range(4):
    angle = i * math.pi/2
    x = (outer_radius - rib_thickness/2.0) * math.cos(angle)
    y = (outer_radius - rib_thickness/2.0) * math.sin(angle)
    rib = cq.Workplane('XY').rect(rib_thickness, rib_height).extrude(body_length)
    rib = rib.translate((x, y, 0))
    merged = merged.union(rib)
# Bolt holes pattern on flange
result = merged
for i in range(bolt_hole_count):
    angle = 2*math.pi*i/bolt_hole_count
    x = (bolt_circle_diameter/2.0)*math.cos(angle)
    y = (bolt_circle_diameter/2.0)*math.sin(angle)
    hole = cq.Workplane('XY').circle(bolt_hole_diameter/2.0).extrude(flange_thickness+2).translate((x,y,-flange_thickness/2.0))
    result = result.cut(hole)
