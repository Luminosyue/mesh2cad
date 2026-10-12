import cadquery as cq
result=cq.Workplane("XY").circle(1).workplane(offset=1).rect(1,1).loft()
