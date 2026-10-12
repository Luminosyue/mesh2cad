import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,32))
w1=cq.Workplane('ZX',origin=(0,-16,0))
r=w0.sketch().segment((-100,11),(-98,10)).arc((-45,-85),(61,-75)).segment((63,-76)).segment((66,-71)).arc((85,-49),(97,-22)).segment((100,-17)).segment((98,-16)).arc((45,80),(-61,75)).segment((-63,76)).segment((-66,71)).arc((-85,49),(-97,22)).close().assemble().push([(0,0)]).circle(85,mode='s').finalize().extrude(-85).union(w1.sketch().push([(0,-1)]).circle(54).circle(41,mode='s').finalize().extrude(100))