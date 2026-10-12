import cadquery as cq
plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
gusset_height = 20.0
gusset_width = 30.0
half_len = plate_length/2
half_wid = plate_width/2
half_gus = gusset_width/2
pts = [
    (-half_len, -half_wid),
    (half_len, -half_wid),
    (half_len, -half_gus),
    (half_len+gusset_height, -half_gus),
    (half_len+gusset_height, half_gus),
    (half_len, half_gus),
    (half_len, half_wid),
    (-half_len, half_wid)
]
result = (cq.Workplane('XY')
          .polyline(pts)
          .close()
          .extrude(plate_thickness))
