import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().arc((-73,-8),(-73,-1),(-72,7)).arc((-81,1),(-73,-8)).assemble().reset().face(w0.sketch().arc((65,0),(81,0),(66,3)).arc((67,1),(65,0)).assemble()).finalize().extrude(-200).union(w0.sketch().arc((1,-8),(4,-2),(1,8)).close().assemble().finalize().extrude(-181))