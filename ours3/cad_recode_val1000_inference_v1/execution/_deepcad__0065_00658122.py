import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,0,0))
r=w0.sketch().segment((-50,41),(-12,25)).segment((-12,19)).segment((-48,12)).segment((-42,-27)).segment((-44,-27)).segment((-44,-54)).segment((-42,-54)).segment((-46,-97)).segment((-12,-99)).segment((-12,-100)).segment((-4,-100)).segment((-4,-99)).segment((8,-100)).segment((8,-96)).segment((43,-92)).segment((41,-65)).segment((4,-69)).segment((4,-67)).segment((-4,-67)).segment((-4,-69)).segment((-24,-67)).segment((-35,-67)).segment((-35,-63)).segment((-44,-62)).segment((-44,-27)).segment((-35,-27)).segment((-35,6)).segment((-12,6)).segment((-12,-27)).segment((10,-27)).segment((10,-47)).segment((47,36)).segment((47,40)).segment((50,40)).segment((50,73)).segment((47,73)).segment((47,93)).segment((39,93)).segment((38,100)).segment((10,95)).segment((10,93)).segment((-22,93)).segment((-22,92)).segment((-45,96)).close().assemble().push([(29,66)]).circle(9,mode='s').finalize().extrude(-1)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0065_00658122.step')
