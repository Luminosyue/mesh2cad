import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-98,0))
w1=cq.Workplane('XY',origin=(0,0,91))
r=w0.sketch().segment((-100,-38),(-48,-100)).segment((-17,-72)).arc((3,-74),(19,-65)).segment((86,-65)).segment((86,-50)).segment((97,-50)).segment((97,-61)).segment((100,-38)).segment((48,14)).segment((17,-22)).arc((-3,-20),(-19,-29)).segment((-86,-29)).segment((-86,-44)).close().assemble().finalize().extrude(18).union(w1.sketch().push([(-42,-60)]).circle(40).circle(38,mode='s').finalize().extrude(-182))