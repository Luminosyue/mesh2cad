import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,36,0))
w1=cq.Workplane('YZ',origin=(34,0,0))
r=w0.sketch().push([(74,55)]).circle(23).circle(22,mode='s').finalize().extrude(-119).union(w0.sketch().segment((-100,-55),(-69,-82)).segment((31,26)).segment((1,54)).close().assemble().finalize().extrude(30)).union(w0.sketch().segment((-85,-66),(-66,-79)).segment((-57,-66)).segment((-57,-65)).segment((-56,-65)).segment((-19,-13)).segment((-48,8)).close().assemble().finalize().extrude(50)).union(w1.workplane(offset=40/2).moveTo(-45,70).cylinder(40,27))