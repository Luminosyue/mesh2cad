import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-30,0))
w1=cq.Workplane('YZ',origin=(30,0,0))
r=w0.sketch().arc((-50,70),(-1,-51),(5,77)).arc((-26,88),(-50,70)).assemble().finalize().extrude(-57).union(w0.sketch().segment((-73,-48),(-20,-89)).segment((74,17)).segment((21,58)).close().assemble().finalize().extrude(-53)).union(w0.sketch().segment((-25,1),(25,1)).arc((0,16),(-25,1)).assemble().finalize().extrude(76)).union(w1.sketch().arc((10,62),(-100,-2),(11,-62)).arc((57,-57),(85,-22)).arc((100,1),(82,22)).arc((50,56),(10,62)).assemble().finalize().extrude(-80))