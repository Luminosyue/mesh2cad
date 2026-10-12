import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,45))
w1=cq.Workplane('YZ',origin=(-33,0,0))
r=w0.workplane(offset=-144/2).cylinder(144,39).union(w0.sketch().segment((-41,80),(-34,-90)).arc((41,-50),(19,33)).segment((19,46)).segment((10,46)).arc((-1,51),(-12,54)).segment((-12,60)).segment((12,60)).segment((12,87)).close().assemble().finalize().extrude(-125)).union(w0.sketch().segment((-38,47),(-35,-60)).arc((41,-10),(-38,47)).assemble().finalize().extrude(43)).union(w1.sketch().push([(1,0)]).circle(99).circle(99,mode='s').finalize().extrude(63))