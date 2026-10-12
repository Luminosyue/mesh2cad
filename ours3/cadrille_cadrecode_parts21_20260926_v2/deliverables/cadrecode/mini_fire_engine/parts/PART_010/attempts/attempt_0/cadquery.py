import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,89,0))
w1=cq.Workplane('ZX',origin=(0,88,0))
r=w0.sketch().segment((-100,5),(-90,-42)).segment((-85,-41)).arc((17,-94),(94,-7)).segment((100,-5)).segment((90,42)).segment((85,41)).arc((-17,94),(-94,7)).close().assemble().circle(94,mode='s').finalize().extrude(-172).union(w0.sketch().segment((-71,64),(-35,-96)).segment((71,-73)).segment((35,96)).close().assemble().finalize().extrude(-172)).union(w1.sketch().circle(95).circle(87,mode='s').finalize().extrude(-176))