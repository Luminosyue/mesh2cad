import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('ZX',origin=(0,-10,0))
r=w0.sketch().segment((-99,-3),(-93,-7)).arc((-65,-55),(-11,-64)).segment((3,-73)).segment((11,-59)).arc((50,-33),(65,13)).segment((73,27)).segment((61,35)).arc((33,83),(-21,93)).segment((-33,100)).segment((-41,86)).arc((-81,60),(-96,14)).segment((-99,14)).close().assemble().finalize().extrude(57).union(w0.sketch().push([(-14,13)]).circle(86).circle(65,mode='s').finalize().extrude(58)).union(w1.workplane(offset=-88/2).moveTo(-45,7).cylinder(88,12))