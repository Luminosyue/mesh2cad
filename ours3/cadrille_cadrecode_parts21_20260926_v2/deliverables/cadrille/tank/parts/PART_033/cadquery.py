import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,27))
w1=cq.Workplane('YZ',origin=(79,0,0))
r=w0.sketch().arc((19,82),(-20,-98),(28,79)).segment((38,87)).segment((25,100)).close().assemble().push([(-1,-10)]).circle(70,mode='s').finalize().extrude(-54).union(w1.sketch().push([(-10,0)]).circle(23).push([(-10.5,0)]).rect(21,18,mode='s').finalize().extrude(-124))