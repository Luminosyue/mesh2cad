import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-11))
w1=cq.Workplane('YZ',origin=(81,0,0))
r=w0.sketch().arc((69,-15),(96,-1),(92,21)).arc((91,16),(89,12)).arc((91,2),(82,-2)).arc((76,-8),(69,-15)).assemble().finalize().extrude(22).union(w1.sketch().segment((-19,-11),(-15,-11)).arc((-14,-6),(-14,-1)).arc((-15,10),(-19,-1)).arc((-20,-6),(-19,-11)).assemble().finalize().extrude(-164))