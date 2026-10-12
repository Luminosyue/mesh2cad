import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-83))
w1=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().segment((-40,-32),(-25,-26)).arc((1,-38),(27,-27)).segment((40,-32)).segment((40,-1)).segment((41,-1)).arc((0,38),(-40,-1)).close().assemble().finalize().extrude(177).union(w1.sketch().push([(0,-3)]).circle(23).push([(0,-3.5)]).rect(22,19,mode='s').finalize().extrude(194))