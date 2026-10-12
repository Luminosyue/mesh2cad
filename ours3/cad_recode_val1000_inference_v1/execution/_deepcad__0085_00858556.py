import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,80,0))
w1=cq.Workplane('ZX',origin=(0,38,0))
r=w0.sketch().arc((-60,-66),(-48,-32),(-60,3)).close().assemble().reset().face(w0.sketch().arc((-36,-93),(0,-100),(36,-93)).close().assemble()).reset().face(w0.sketch().segment((-36,93),(36,93)).arc((0,100),(-36,93)).assemble()).reset().face(w0.sketch().arc((38,-89),(100,0),(38,89)).segment((38,45)).arc((60,0),(38,-45)).close().assemble()).finalize().extrude(-160).union(w0.sketch().arc((-99,-10),(-98,-10),(-98,-11)).arc((-79,-50),(-42,-75)).arc((-39,-73),(-36,-72)).arc((-10,58),(44,-60)).arc((57,-71),(68,-84)).arc((16,92),(-99,-10)).assemble().finalize().extrude(-121)).union(w1.workplane(offset=-79/2).moveTo(-55,23).cylinder(79,4))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0085_00858556.step')
