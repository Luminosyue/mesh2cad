import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-9))
r=w0.sketch().segment((-51,98),(-41,72)).segment((-35,74)).segment((-45,100)).close().assemble().push([(44,-90)]).circle(10).finalize().extrude(5).union(w0.sketch().arc((-41,-40),(-3,-93),(40,-44)).segment((41,-44)).segment((41,44)).segment((39,44)).arc((0,92),(-39,44)).segment((-41,44)).close().assemble().finalize().extrude(18))