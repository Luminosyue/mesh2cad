import cadquery as cq
w0=cq.Workplane('YZ',origin=(53,0,0))
r=w0.sketch().segment((-100,-61),(-99,-61)).segment((-99,-49)).segment((-63,-49)).segment((-63,-61)).segment((100,-61)).segment((100,61)).segment((-100,61)).close().assemble().push([(16.5,-50.5)]).rect(141,3,mode='s').finalize().extrude(-106)