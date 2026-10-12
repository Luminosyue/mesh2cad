import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-14))
r=w0.sketch().push([(-85.5,0)]).rect(29,72).push([(0,-27.5)]).rect(28,17).reset().face(w0.sketch().segment((-14,2),(14,2)).segment((14,-36)).segment((15,-36)).segment((15,-34)).segment((14,-34)).segment((14,36)).segment((-11,36)).arc((-12,32),(-14,27)).close().assemble()).reset().face(w0.sketch().segment((71,-31),(72,-31)).segment((72,-36)).segment((97,-36)).segment((97,-31)).segment((100,-31)).segment((100,31)).segment((97,31)).segment((97,36)).segment((72,36)).segment((72,31)).segment((71,31)).close().assemble()).finalize().extrude(28)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0025_00254560.step')
