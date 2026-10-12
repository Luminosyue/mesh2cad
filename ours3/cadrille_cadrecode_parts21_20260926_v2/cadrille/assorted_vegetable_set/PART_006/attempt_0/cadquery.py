import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-13))
w1=cq.Workplane('YZ',origin=(49,0,0))
r=w0.sketch().push([(-25,0)]).circle(75).circle(63,mode='s').finalize().extrude(-1).union(w0.sketch().push([(52,0)]).circle(48).circle(41,mode='s').finalize().extrude(10)).union(w0.sketch().segment((40,-26),(83,-48)).segment((94,-27)).segment((51,-5)).close().assemble().push([(67,-27)]).circle(10,mode='s').finalize().extrude(27)).union(w1.sketch().push([(0,-8)]).circle(6).push([(0,-7.5)]).rect(2,7,mode='s').finalize().extrude(36))