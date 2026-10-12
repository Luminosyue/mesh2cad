import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-82,0))
w1=cq.Workplane('ZX',origin=(0,-60,0))
r=w0.sketch().segment((-95,43),(-91,43)).segment((-91,-40)).arc((98,19),(-95,43)).assemble().finalize().extrude(159).union(w0.workplane(offset=164/2).moveTo(-1,0).cylinder(164,90)).union(w1.sketch().arc((-99,18),(99,-20),(-98,23)).arc((-96,20),(-99,18)).assemble().finalize().extrude(128))