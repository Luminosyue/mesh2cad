import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-32,0))
r=w0.sketch().segment((-100,-44),(-75,-89)).segment((-2,-46)).segment((-27,-3)).close().assemble().finalize().extrude(63).union(w0.sketch().segment((-62,-4),(-20,-46)).segment((100,47)).segment((58,89)).close().assemble().finalize().extrude(64))