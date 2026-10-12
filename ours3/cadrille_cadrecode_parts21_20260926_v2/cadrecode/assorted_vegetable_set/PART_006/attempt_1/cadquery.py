import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-13))
w1=cq.Workplane('XY',origin=(0,0,-16))
r=w0.sketch().segment((-74,-56),(-68,-56)).segment((-68,-58)).segment((-69,-58)).arc((23,67),(-74,-56)).assemble().push([(-22,1)]).circle(52,mode='s').finalize().extrude(11).union(w0.sketch().segment((31,-36),(67,-61)).segment((100,-10)).segment((91,-3)).segment((91,33)).segment((66,33)).segment((66,25)).segment((55,34)).close().assemble().push([(65,-14)]).circle(15,mode='s').finalize().extrude(22)).union(w1.sketch().push([(-22,1)]).circle(56).circle(56,mode='s').finalize().extrude(13))