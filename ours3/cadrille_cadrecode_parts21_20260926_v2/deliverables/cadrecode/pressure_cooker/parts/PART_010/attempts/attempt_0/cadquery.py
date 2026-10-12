import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-24,0))
w1=cq.Workplane('XY',origin=(0,0,-21))
r=w0.workplane(offset=-76/2).moveTo(0,-1).cylinder(76,34).union(w0.workplane(offset=70/2).moveTo(0,-1).cylinder(70,65)).union(w0.workplane(offset=107/2).moveTo(0,-1).cylinder(107,60)).union(w1.sketch().arc((-46,55),(-58,-76),(69,-55)).arc((71,-54),(72,-53)).segment((72,-49)).segment((74,-49)).arc((81,-41),(86,-31)).arc((96,0),(86,31)).arc((81,41),(72,50)).segment((72,55)).segment((69,55)).arc((15,95),(-46,68)).close().assemble().finalize().extrude(45))