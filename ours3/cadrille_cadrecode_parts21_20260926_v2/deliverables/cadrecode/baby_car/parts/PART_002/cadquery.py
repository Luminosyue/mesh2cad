import cadquery as cq
w0=cq.Workplane('YZ',origin=(-7,0,0))
w1=cq.Workplane('ZX',origin=(0,16,0))
r=w0.workplane(offset=-25/2).moveTo(47,0).cylinder(25,35).union(w0.sketch().segment((-100,1),(-95,-1)).arc((-68,-45),(-17,-33)).segment((-12,-35)).segment((-2,1)).arc((99,-7),(-1,10)).segment((-10,13)).arc((-37,48),(-79,37)).segment((-84,39)).close().assemble().finalize().extrude(22)).union(w0.sketch().segment((-51,-16),(-40,-22)).segment((-10,29)).segment((-21,35)).close().assemble().finalize().extrude(39)).union(w1.sketch().push([(2,-3)]).circle(28).circle(24,mode='s').finalize().extrude(-106))