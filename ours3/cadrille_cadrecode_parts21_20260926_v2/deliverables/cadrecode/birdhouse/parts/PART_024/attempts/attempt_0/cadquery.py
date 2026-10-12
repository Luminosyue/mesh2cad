import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-91,53),(-39,-4)).arc((-57,20),(-91,53)).assemble().reset().face(w0.sketch().segment((26,7),(90,-54)).segment((91,-53)).segment((28,9)).arc((27,8),(26,7)).assemble()).finalize().extrude(-200).union(w0.workplane(offset=-114/2).moveTo(65,52).cylinder(114,1))