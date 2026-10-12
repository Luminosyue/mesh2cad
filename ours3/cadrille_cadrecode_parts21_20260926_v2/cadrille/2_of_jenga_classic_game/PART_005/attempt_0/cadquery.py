import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-92))
w1=cq.Workplane('ZX',origin=(0,98,0))
r=w0.sketch().segment((-98,-93),(94,-95)).segment((98,97)).segment((-94,100)).close().assemble().push([(0,2)]).circle(34,mode='s').finalize().extrude(41).union(w1.sketch().segment((53,-91),(92,-91)).segment((92,91)).arc((73,95),(53,94)).segment((53,41)).arc((54,36),(55,31)).segment((91,31)).segment((91,-31)).segment((55,-31)).arc((54,-36),(53,-41)).close().assemble().finalize().extrude(-195))