import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-36,0))
w1=cq.Workplane('YZ',origin=(43,0,0))
r=w0.sketch().arc((-73,44),(-18,-48),(70,10)).arc((98,31),(65,39)).arc((49,47),(31,48)).arc((-20,44),(-73,44)).assemble().finalize().extrude(94).union(w0.sketch().segment((-55,25),(55,25)).arc((0,47),(-55,25)).assemble().finalize().extrude(128)).union(w1.sketch().arc((-93,-10),(72,-57),(-45,70)).arc((-90,37),(-93,-10)).assemble().finalize().extrude(-44))