import cadquery as cq
w0=cq.Workplane('YZ',origin=(-34,0,0))
w1=cq.Workplane('XY',origin=(0,0,42))
r=w0.sketch().segment((-99,20),(-96,16)).arc((-85,-46),(-37,-87)).segment((-34,-92)).segment((-29,-90)).arc((46,-83),(94,-23)).segment((99,-20)).segment((96,-16)).arc((85,46),(37,87)).segment((34,92)).segment((29,90)).arc((-46,83),(-94,23)).close().assemble().finalize().extrude(56).union(w1.workplane(offset=-86/2).cylinder(86,99))