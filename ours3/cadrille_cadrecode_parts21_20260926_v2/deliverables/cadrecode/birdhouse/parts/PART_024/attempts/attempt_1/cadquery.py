import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-91,53),(-39,-4)).segment((-43,2)).segment((-88,54)).close().assemble().reset().face(w0.sketch().segment((26,7),(90,-54)).segment((91,-53)).segment((28,9)).close().assemble()).finalize().extrude(-200).union(w0.workplane(offset=-120/2).moveTo(66,52).cylinder(120,1))