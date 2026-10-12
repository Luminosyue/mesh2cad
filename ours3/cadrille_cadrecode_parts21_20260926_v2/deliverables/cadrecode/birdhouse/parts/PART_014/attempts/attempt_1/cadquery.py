import cadquery as cq
w0=cq.Workplane('YZ',origin=(97,0,0))
r=w0.sketch().segment((-56,-99),(-54,-100)).segment((56,8)).segment((54,10)).close().assemble().reset().face(w0.sketch().segment((-56,95),(54,10)).segment((56,8)).segment((58,5)).segment((54,10)).segment((54,11)).segment((-54,100)).close().assemble()).finalize().extrude(-193)