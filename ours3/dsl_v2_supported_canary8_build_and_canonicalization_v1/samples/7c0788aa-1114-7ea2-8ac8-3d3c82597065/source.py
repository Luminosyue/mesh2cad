import cadquery as cq
plate = cq.Workplane('XY').rect(80,60).extrude(6)
result = plate.edges('|Z').chamfer(1)
