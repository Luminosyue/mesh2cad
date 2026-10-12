import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-99,0))
w1=cq.Workplane('YZ',origin=(-58,0,0))
r=w0.sketch().segment((18,-77),(34,-100)).segment((62,-84)).segment((46,-60)).close().assemble().finalize().extrude(199).union(w1.sketch().segment((-99,-97),(-95,-97)).arc((-76,-96),(-57,-97)).segment((97,-99)).segment((97,-97)).segment((98,-97)).segment((98,-82)).arc((99,-70),(98,-58)).segment((98,1)).segment((94,1)).arc((0,58),(-95,1)).segment((-99,1)).segment((-99,-58)).arc((-100,-70),(-99,-82)).close().assemble().finalize().extrude(-25))