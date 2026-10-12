import cadquery as cq
w0=cq.Workplane('YZ',origin=(77,0,0))
w1=cq.Workplane('YZ',origin=(72,0,0))
r=w0.sketch().segment((-21,-95),(-17,-95)).segment((-17,-99)).segment((17,-100)).segment((17,-95)).segment((21,-95)).segment((21,-5)).segment((17,-5)).segment((17,84)).segment((-20,84)).arc((21,44),(-21,6)).segment((-21,-5)).arc((-19,0),(-17,5)).segment((-17,-5)).segment((-21,-5)).segment((-21,-10)).arc((-18,-45),(-21,-80)).close().assemble().finalize().extrude(-153).union(w1.workplane(offset=-144/2).moveTo(16,0).box(2,158,144))