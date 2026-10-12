import cadquery as cq
w0=cq.Workplane('YZ',origin=(-51,0,0))
w1=cq.Workplane('ZX',origin=(0,88,0))
r=w0.sketch().arc((-40,-31),(-14,-99),(44,-54)).arc((31,97),(-40,-31)).assemble().finalize().extrude(58).union(w0.sketch().arc((-98,-3),(10,-92),(93,25)).close().assemble().finalize().extrude(98)).union(w1.sketch().arc((-32,50),(-68,-39),(27,-41)).arc((54,31),(-19,46)).arc((-25,46),(-32,50)).assemble().finalize().extrude(-168))