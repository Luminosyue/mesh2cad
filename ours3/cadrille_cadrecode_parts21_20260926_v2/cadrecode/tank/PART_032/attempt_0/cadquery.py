import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-34))
w1=cq.Workplane('YZ',origin=(0,0,0))
r=w0.workplane(offset=53/2).moveTo(0,10).cylinder(53,82).union(w0.sketch().segment((-66,74),(-65,69)).arc((-84,-23),(1,-66)).segment((2,-71)).segment((51,-61)).segment((50,-56)).arc((69,55),(-45,89)).segment((-46,90)).close().assemble().finalize().extrude(57)).union(w0.workplane(offset=57/2).moveTo(0,10).cylinder(57,77)).union(w1.workplane(offset=31/2).moveTo(-83,20).cylinder(31,13))