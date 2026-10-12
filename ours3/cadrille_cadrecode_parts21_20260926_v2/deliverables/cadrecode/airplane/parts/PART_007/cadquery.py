import cadquery as cq
w0=cq.Workplane('YZ',origin=(33,0,0))
w1=cq.Workplane('YZ',origin=(83,0,0))
r=w0.sketch().segment((2,-4),(75,-11)).segment((76,-8)).segment((2,0)).close().assemble().finalize().extrude(-133).union(w0.sketch().segment((-50,5),(70,-20)).segment((74,-2)).segment((-46,16)).close().assemble().finalize().extrude(-111)).union(w0.sketch().segment((-89,7),(65,-19)).segment((66,-10)).segment((63,-10)).segment((63,-3)).segment((-88,21)).close().assemble().finalize().extrude(51)).union(w1.workplane(offset=12/2).moveTo(36,-5).cylinder(12,10))