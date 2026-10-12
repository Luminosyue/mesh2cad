import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-34))
w1=cq.Workplane('YZ',origin=(0,0,0))
r=w0.sketch().arc((-54,69),(-79,-30),(19,-65)).arc((79,43),(-43,80)).segment((-43,69)).close().assemble().finalize().extrude(53).union(w0.sketch().segment((-65,-51),(-56,-51)).arc((0,-74),(56,-51)).segment((65,-51)).segment((65,-40)).arc((74,-12),(72,18)).arc((70,56),(40,80)).arc((-7,99),(-56,83)).segment((-65,83)).segment((-65,72)).arc((-80,16),(-50,-35)).segment((-65,-35)).close().assemble().finalize().extrude(57)).union(w1.workplane(offset=32/2).moveTo(-83,21).cylinder(32,17))