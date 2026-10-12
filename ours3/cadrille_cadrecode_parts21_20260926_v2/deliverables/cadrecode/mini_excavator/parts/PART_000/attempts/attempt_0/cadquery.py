import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-11,0))
w1=cq.Workplane('XY',origin=(0,0,-41))
r=w0.sketch().segment((-66,-49),(66,-30)).segment((66,54)).segment((-66,54)).close().assemble().finalize().extrude(-77).union(w0.sketch().segment((-100,-1),(-95,-1)).arc((-61,-50),(-1,-38)).arc((99,10),(-8,35)).arc((-59,50),(-95,11)).segment((-100,11)).close().assemble().finalize().extrude(49)).union(w0.workplane(offset=106/2).moveTo(-6,-1).cylinder(106,53)).union(w1.sketch().arc((-37,10),(-16,-99),(48,-7)).arc((16,95),(-37,10)).assemble().finalize().extrude(108))