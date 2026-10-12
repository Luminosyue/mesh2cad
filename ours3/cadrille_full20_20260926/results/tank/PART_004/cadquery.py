import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-84))
w1=cq.Workplane('YZ',origin=(-47,0,0))
r=w0.sketch().segment((-99,-94),(-21,-94)).segment((-21,-47)).segment((-30,-47)).arc((-59,-74),(-99,-62)).close().assemble().finalize().extrude(110).union(w0.sketch().push([(-59,-62)]).circle(38).circle(33,mode='s').finalize().extrude(179)).union(w0.workplane(offset=183/2).moveTo(-59,-62).cylinder(183,38)).union(w1.sketch().push([(-65,-82)]).circle(18).circle(9,mode='s').finalize().extrude(-71))