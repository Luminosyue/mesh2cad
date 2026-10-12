import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,92,0))
r=w0.workplane(offset=-184/2).box(200,78,184)