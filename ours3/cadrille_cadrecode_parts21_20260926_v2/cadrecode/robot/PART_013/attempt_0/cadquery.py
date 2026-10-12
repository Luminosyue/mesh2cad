import cadquery as cq
w0=cq.Workplane('YZ',origin=(-28,0,0))
w1=cq.Workplane('ZX',origin=(0,-32,0))
r=w0.sketch().arc((-47,1),(1,-72),(42,6)).arc((-2,72),(-47,1)).assemble().finalize().extrude(-60).union(w0.sketch().arc((-40,8),(1,-74),(38,11)).arc((-2,98),(-40,8)).assemble().finalize().extrude(101)).union(w1.sketch().arc((-41,84),(17,-95),(-1,99)).arc((-21,96),(-41,84)).assemble().finalize().extrude(73))