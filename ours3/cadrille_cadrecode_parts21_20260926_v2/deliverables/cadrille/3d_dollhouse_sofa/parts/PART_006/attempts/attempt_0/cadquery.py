import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,99,0))
r=w0.workplane(offset=-199/2).moveTo(57,-1).cylinder(199,19).union(w0.sketch().segment((-80,-16),(66,-21)).segment((67,5)).segment((-79,9)).close().assemble().finalize().extrude(-197)).union(w0.sketch().segment((-76,-18),(65,-21)).segment((66,4)).segment((-76,8)).close().assemble().finalize().extrude(1))