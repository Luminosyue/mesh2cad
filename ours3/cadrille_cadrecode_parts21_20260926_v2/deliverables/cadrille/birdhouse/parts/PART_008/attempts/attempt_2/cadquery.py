import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-94))
w1=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().segment((20,-38),(38,-37)).segment((38,-22)).segment((20,-23)).close().assemble().finalize().extrude(8).union(w0.sketch().segment((-9,-11),(27,-13)).segment((27,-7)).segment((-8,-5)).close().assemble().finalize().extrude(189)).union(w1.sketch().arc((-40,39),(-41,24),(-34,11)).segment((-34,25)).segment((-5,25)).arc((-22,34),(-40,39)).assemble().finalize().extrude(200))