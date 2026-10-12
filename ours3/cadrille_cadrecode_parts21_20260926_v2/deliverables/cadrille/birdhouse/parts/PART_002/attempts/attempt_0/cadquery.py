import cadquery as cq
w0=cq.Workplane('YZ',origin=(51,0,0))
w1=cq.Workplane('ZX',origin=(0,51,0))
r=w0.sketch().push([(37,0)]).circle(63).circle(36,mode='s').finalize().extrude(-101).union(w0.sketch().segment((-100,56),(-99,-64)).segment((24,-63)).segment((24,-40)).arc((37,-34),(48,-25)).segment((64,-25)).segment((64,25)).segment((48,25)).arc((37,34),(24,40)).segment((24,63)).close().assemble().push([(-28,0)]).rect(110,72,mode='s').finalize().extrude(-100)).union(w1.sketch().push([(0,40)]).circle(11).push([(0,40.5)]).rect(12,11,mode='s').finalize().extrude(-128))