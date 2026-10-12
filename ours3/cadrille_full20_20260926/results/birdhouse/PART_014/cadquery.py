import cadquery as cq
w0=cq.Workplane('YZ',origin=(94,0,0))
r=w0.sketch().segment((-98,-94),(-96,-100)).segment((17,4)).segment((17,11)).close().assemble().finalize().extrude(-193).union(w0.sketch().segment((-98,94),(17,2)).segment((17,5)).segment((-96,100)).close().assemble().finalize().extrude(-192))