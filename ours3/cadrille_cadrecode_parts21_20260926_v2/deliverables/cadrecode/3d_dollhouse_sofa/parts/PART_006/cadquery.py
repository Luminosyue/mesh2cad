import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,99,0))
r=w0.sketch().arc((44,10),(73,-15),(45,12)).segment((45,10)).close().assemble().finalize().extrude(-199).union(w0.sketch().segment((-80,-16),(65,-21)).segment((65,4)).segment((-79,9)).close().assemble().finalize().extrude(-197)).union(w0.workplane(offset=1/2).moveTo(-27,-6).cylinder(1,15))