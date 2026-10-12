import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-91,52),(-43,0)).segment((-41,1)).segment((-89,54)).close().assemble().reset().face(w0.sketch().segment((26,7),(90,-54)).segment((91,-52)).segment((29,9)).close().assemble()).push([(65,52)]).circle(1).finalize().extrude(-200)