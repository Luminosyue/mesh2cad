import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,8,0))
r=w0.sketch().segment((-54,-98),(-40,-98)).segment((-40,-100)).segment((12,-100)).segment((12,-98)).segment((19,-98)).segment((19,-79)).segment((47,-97)).segment((54,-83)).segment((54,-3)).segment((49,-2)).segment((49,-48)).segment((12,-46)).segment((12,-28)).segment((-22,-28)).segment((-22,27)).segment((-34,36)).segment((-22,51)).segment((-22,57)).segment((-54,57)).close().assemble().reset().face(w0.sketch().segment((-54,-80),(-22,-45)).segment((-22,-46)).segment((-8,-46)).segment((-8,-62)).segment((19,-46)).segment((12,-37)).segment((12,-46)).segment((-8,-46)).segment((-8,-62)).segment((-54,-80)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-54,44),(-22,44)).segment((-22,57)).segment((12,57)).segment((12,51)).segment((27,57)).segment((49,57)).segment((49,47)).segment((54,47)).segment((54,100)).segment((-54,100)).close().assemble()).finalize().extrude(-16)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0062_00623888.step')
