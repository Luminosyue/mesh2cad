import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-47))
w1=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().push([(10,0)]).circle(57).circle(37,mode='s').finalize().extrude(-42).union(w0.workplane(offset=145/2).cylinder(145,85)).union(w0.sketch().segment((-31,75),(-29,29)).arc((-34,0),(-25,-29)).segment((-23,-75)).segment((31,-75)).segment((29,-29)).arc((34,0),(25,29)).segment((23,75)).close().assemble().finalize().extrude(147)).union(w1.sketch().push([(10,0)]).circle(39).circle(13,mode='s').finalize().extrude(190))