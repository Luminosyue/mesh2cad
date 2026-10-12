import cadquery as cq
w0=cq.Workplane('YZ',origin=(-43,0,0))
w1=cq.Workplane('XY',origin=(0,0,51))
r=w0.sketch().segment((-99,63),(-98,63)).arc((-61,29),(-24,63)).segment((-23,63)).segment((-23,67)).segment((-24,67)).arc((-61,100),(-98,67)).segment((-99,67)).close().assemble().finalize().extrude(-52).union(w0.sketch().segment((-88,19),(-34,-100)).segment((14,-78)).segment((-40,41)).close().assemble().finalize().extrude(-46)).union(w1.sketch().push([(-60,-49)]).circle(38).circle(37,mode='s').finalize().extrude(-82))