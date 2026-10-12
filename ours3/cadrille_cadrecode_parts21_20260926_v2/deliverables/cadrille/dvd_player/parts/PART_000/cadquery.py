import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-14,0))
r=w0.sketch().segment((-50,-99),(-40,-99)).segment((-40,-100)).segment((40,-100)).segment((40,-99)).segment((50,-99)).segment((50,-61)).arc((47,-59),(50,-57)).segment((50,99)).segment((40,99)).segment((40,100)).segment((-40,100)).segment((-40,99)).segment((-50,99)).close().assemble().finalize().extrude(29)