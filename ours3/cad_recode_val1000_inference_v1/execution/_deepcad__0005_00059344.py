import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(93,0,0))
r=w0.sketch().segment((-50,-90),(-49,-90)).arc((-48,-88),(-47,-87)).arc((-48,-70),(-49,-53)).arc((-50,-52),(-50,-50)).close().assemble().reset().face(w0.sketch().arc((-50,-19),(-49,-17),(-49,-15)).segment((-50,-15)).close().assemble()).reset().face(w0.sketch().arc((-50,50),(-49,52),(-47,53)).arc((-48,55),(-49,57)).segment((-50,57)).close().assemble()).reset().face(w0.sketch().segment((-26,-100),(44,-100)).arc((43,-98),(43,-96)).arc((10,-98),(-22,-93)).arc((-24,-96),(-26,-100)).assemble()).reset().face(w0.sketch().arc((-50,57),(-49,55),(-49,53)).arc((-48,52),(-47,50)).arc((-48,52),(-50,53)).close().assemble()).push([(0,58.5)]).rect(100,83).push([(0,33)]).circle(17,mode='s').finalize().extrude(-186)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0005_00059344.step')
