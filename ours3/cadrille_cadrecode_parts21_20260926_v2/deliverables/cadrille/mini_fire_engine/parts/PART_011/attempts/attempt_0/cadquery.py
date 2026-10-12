import cadquery as cq
w0=cq.Workplane('YZ',origin=(-51,0,0))
w1=cq.Workplane('YZ',origin=(-49,0,0))
r=w0.sketch().segment((-100,-12),(-96,-13)).arc((-16,-97),(84,-40)).segment((89,-41)).segment((100,12)).segment((96,13)).arc((16,97),(-84,40)).segment((-89,41)).close().assemble().finalize().extrude(87).union(w0.sketch().arc((-33,61),(-1,-97),(33,61)).close().assemble().finalize().extrude(102)).union(w1.sketch().circle(98).circle(58,mode='s').finalize().extrude(99))