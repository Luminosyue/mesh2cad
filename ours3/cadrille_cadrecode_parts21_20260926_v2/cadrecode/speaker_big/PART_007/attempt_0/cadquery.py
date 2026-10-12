import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-74,0))
w1=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().segment((-98,-45),(-50,-45)).arc((-40,-45),(-30,-45)).segment((99,-45)).segment((99,45)).segment((69,45)).arc((34,44),(-1,45)).segment((-98,45)).close().assemble().finalize().extrude(149).union(w1.sketch().push([(13,-14)]).circle(13).push([(13,-13.5)]).rect(12,13,mode='s').finalize().extrude(172))