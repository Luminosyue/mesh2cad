import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-92))
w1=cq.Workplane('YZ',origin=(90,0,0))
r=w0.sketch().segment((-97,-93),(93,-95)).segment((97,97)).segment((-93,100)).close().assemble().push([(0,2)]).circle(28,mode='s').finalize().extrude(41).union(w0.workplane(offset=41/2).moveTo(0,2).cylinder(41,82)).union(w1.sketch().arc((-99,87),(-99,62),(-95,54)).segment((95,54)).arc((99,78),(90,99)).segment((90,90)).segment((6,90)).segment((6,92)).segment((-99,92)).arc((-100,89),(-99,87)).assemble().push([(0,56)]).circle(2,mode='s').finalize().extrude(-186))