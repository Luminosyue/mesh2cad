import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-7))
w1=cq.Workplane('YZ',origin=(79,0,0))
r=w0.sketch().arc((68,9),(70,6),(71,2)).segment((80,-14)).segment((90,-7)).segment((83,3)).arc((98,19),(77,13)).close().assemble().reset().face(w0.sketch().segment((74,10),(82,-1)).segment((92,6)).segment((84,17)).close().assemble(),mode='s').finalize().extrude(19).union(w1.sketch().arc((-26,-10),(-24,-12),(-24,-14)).arc((-21,-14),(-19,-14)).arc((-18,-4),(-20,10)).arc((-22,12),(-24,14)).arc((-26,10),(-26,6)).close().assemble().finalize().extrude(-179))