import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-65))
w1=cq.Workplane('ZX',origin=(0,29,0))
r=w0.sketch().segment((-81,-79),(78,-80)).segment((80,16)).arc((97,58),(55,77)).segment((55,84)).segment((-78,84)).segment((-78,74)).segment((-80,74)).close().assemble().finalize().extrude(52).union(w0.sketch().arc((-80,10),(-79,-27),(-59,-58)).arc((-45,-82),(-18,-81)).arc((99,1),(-35,43)).arc((-86,52),(-80,10)).assemble().finalize().extrude(93)).union(w1.sketch().arc((-66,62),(53,-1),(-50,78)).segment((-50,62)).close().assemble().finalize().extrude(-104))