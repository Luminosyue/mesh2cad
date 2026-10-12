import cadquery as cq
result=cq.Workplane("XY").polyline([[0,0],[1,0],[0,1]]).close().extrude(2)
