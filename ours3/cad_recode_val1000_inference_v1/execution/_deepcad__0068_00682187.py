import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-97,-70),(-90,-70)).segment((-97,-57)).close().assemble().reset().face(w0.sketch().segment((-97,-55),(-97,55)).arc((-100,0),(-97,-55)).assemble()).reset().face(w0.sketch().segment((-90,70),(-83,70)).segment((-83,83)).segment((97,83)).segment((97,13)).segment((90,13)).segment((97,28)).segment((97,70)).segment((83,70)).segment((83,83)).segment((-83,83)).close().assemble()).reset().face(w0.sketch().segment((-41,-17),(-39,-19)).segment((-14,13)).segment((14,13)).close().assemble()).finalize().extrude(180).union(w0.sketch().segment((-65,-46),(-64,-46)).arc((-55,-35),(-43,-27)).segment((-43,-14)).segment((-38,-14)).segment((-38,-27)).arc((-26,-35),(-17,-46)).segment((-16,-46)).arc((-41,-10),(-65,30)).close().assemble().finalize().extrude(199))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00682187.step')
