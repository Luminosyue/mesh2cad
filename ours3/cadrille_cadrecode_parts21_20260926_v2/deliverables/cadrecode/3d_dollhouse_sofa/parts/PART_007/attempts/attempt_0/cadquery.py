import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-99,0))
w1=cq.Workplane('YZ',origin=(21,0,0))
r=w0.sketch().segment((-81,-5),(39,-5)).arc((79,-4),(40,0)).segment((-81,0)).close().assemble().finalize().extrude(199).union(w1.sketch().segment((-99,-77),(97,-81)).segment((97,-59)).segment((98,-59)).segment((98,-1)).segment((97,-1)).segment((97,43)).segment((-99,43)).close().assemble().finalize().extrude(-25))