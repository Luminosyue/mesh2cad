import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,91,0))
w1=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-58,8),(-57,7)).arc((-48,-26),(-20,-46)).segment((-19,-47)).segment((-18,-46)).arc((26,-38),(46,2)).segment((47,3)).segment((46,4)).arc((37,37),(9,56)).segment((8,57)).segment((7,56)).arc((-37,40),(-57,8)).close().assemble().push([(-5,0)]).circle(45,mode='s').finalize().extrude(-186).union(w0.workplane(offset=4/2).moveTo(8,0).cylinder(4,51)).union(w1.sketch().arc((-37,4),(-36,13),(-34,22)).arc((-37,13),(-37,4)).assemble().finalize().extrude(-200))