import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,88))
w1=cq.Workplane('YZ',origin=(-8,0,0))
r=w0.sketch().segment((-11,-72),(4,-72)).segment((4,-69)).segment((9,-88)).segment((23,-85)).segment((-1,88)).segment((-11,86)).segment((-11,80)).arc((-19,63),(-11,46)).close().assemble().finalize().extrude(-165).union(w0.sketch().segment((-12,-72),(12,-72)).segment((12,-49)).arc((0,-52),(-12,-49)).close().assemble().finalize().extrude(-162)).union(w1.sketch().arc((38,-100),(59,-77),(88,-67)).arc((33,-42),(38,-100)).assemble().finalize().extrude(12))