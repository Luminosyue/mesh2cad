import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-14,0))
r=w0.sketch().segment((-46,-87),(-41,-87)).segment((-41,-100)).segment((42,-100)).segment((42,-87)).segment((46,-87)).segment((46,54)).segment((42,54)).segment((42,67)).segment((46,67)).segment((46,96)).segment((42,96)).segment((42,100)).segment((-41,100)).segment((-41,96)).segment((-46,96)).segment((-46,86)).segment((-37,86)).segment((-37,73)).segment((14,73)).segment((14,-73)).segment((-37,-73)).segment((-37,-76)).segment((-46,-76)).close().assemble().finalize().extrude(28)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0055_00550804.step')
