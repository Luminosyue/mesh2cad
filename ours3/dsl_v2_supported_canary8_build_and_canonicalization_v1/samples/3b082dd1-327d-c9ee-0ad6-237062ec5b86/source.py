import cadquery as cq

result = cq.Workplane('XY').box(80,40,20, centered=(True,True,False)).edges('|Z').fillet(1.0)
