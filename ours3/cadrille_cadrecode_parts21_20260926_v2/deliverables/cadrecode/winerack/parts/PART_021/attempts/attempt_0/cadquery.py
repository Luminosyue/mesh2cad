import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-8,-5),(8,-5)).segment((8,5)).segment((-8,5)).segment((-8,0)).segment((-7,0)).segment((-7,-2)).segment((-8,-2)).close().assemble().push([(4,2)]).circle(2,mode='s').finalize().extrude(200)