import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
w1=cq.Workplane('YZ',origin=(51,0,0))
r=w0.sketch().segment((-91,52),(-39,-4)).segment((-38,-2)).segment((-89,54)).close().assemble().reset().face(w0.sketch().segment((26,8),(90,-54)).segment((91,-52)).segment((29,8)).close().assemble()).finalize().extrude(-200).union(w1.workplane(offset=-70/2).moveTo(65,52).cylinder(70,1))