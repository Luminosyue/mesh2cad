import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,21))
w1=cq.Workplane('ZX',origin=(0,-40,0))
r=w0.sketch().segment((-20,-95),(12,-100)).segment((13,-94)).arc((59,-78),(89,-38)).segment((89,-37)).segment((99,10)).segment((67,16)).arc((55,-65),(-20,-79)).close().assemble().finalize().extrude(-74).union(w0.sketch().push([(-2,0)]).circle(95).circle(83,mode='s').finalize().extrude(-65)).union(w1.sketch().push([(10,0)]).circle(44).circle(31,mode='s').finalize().extrude(124))