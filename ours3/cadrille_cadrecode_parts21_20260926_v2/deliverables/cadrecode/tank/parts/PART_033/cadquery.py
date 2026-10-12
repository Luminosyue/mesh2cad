import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,16))
w1=cq.Workplane('XY',origin=(0,0,28))
r=w0.sketch().segment((-28,76),(13,-100)).segment((28,-97)).segment((-13,78)).close().assemble().push([(25,86)]).circle(14).finalize().extrude(-44).union(w0.sketch().push([(0,-9)]).circle(91).circle(64,mode='s').finalize().extrude(-26)).union(w1.sketch().arc((-77,10),(-77,-56),(-16,-74)).arc((86,26),(-59,40)).arc((-83,30),(-77,10)).assemble().push([(5,-15)]).circle(52,mode='s').finalize().extrude(-55))