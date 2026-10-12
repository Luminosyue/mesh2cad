import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-74,0))
r=w0.sketch().segment((-100,6),(-98,4)).segment((-97,-45)).segment((99,-45)).segment((99,-37)).segment((100,-36)).segment((99,-34)).segment((99,45)).segment((-97,45)).segment((-97,13)).close().assemble().finalize().extrude(149)