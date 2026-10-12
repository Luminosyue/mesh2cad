import cadquery as cq
w0=cq.Workplane('YZ',origin=(-39,0,0))
w1=cq.Workplane('ZX',origin=(0,33,0))
r=w0.sketch().arc((-85,-46),(-76,-62),(-63,-76)).segment((-63,-75)).segment((-61,-75)).segment((-61,-79)).arc((99,1),(-72,66)).arc((-72,59),(-78,57)).arc((-99,6),(-85,-46)).assemble().finalize().extrude(32).union(w0.sketch().arc((-33,50),(26,-59),(11,64)).arc((-18,71),(-33,50)).assemble().finalize().extrude(92)).union(w1.sketch().arc((-42,53),(-89,-10),(-14,-35)).arc((97,-20),(10,48)).arc((-1,54),(-13,58)).segment((-13,53)).close().assemble().finalize().extrude(-78))