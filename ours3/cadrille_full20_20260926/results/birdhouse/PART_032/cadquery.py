import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-99))
w1=cq.Workplane('YZ',origin=(-85,0,0))
r=w0.sketch().segment((-100,-93),(100,-93)).segment((100,-68)).segment((80,-68)).segment((80,-92)).segment((-80,-92)).segment((-80,-68)).segment((-100,-68)).close().assemble().finalize().extrude(161).union(w0.sketch().segment((-99,-47),(32,-28)).arc((-1,-5),(-26,24)).segment((-99,18)).close().assemble().finalize().extrude(161)).union(w1.sketch().arc((-92,62),(-86,69),(-92,77)).close().assemble().finalize().extrude(165))