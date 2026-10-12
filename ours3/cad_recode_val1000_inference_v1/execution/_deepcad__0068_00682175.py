import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
w1=cq.Workplane('ZX',origin=(0,47,0))
r=w0.sketch().segment((-100,-79),(-91,-79)).segment((-91,-86)).segment((97,-86)).segment((-100,86)).close().assemble().finalize().extrude(-198).union(w0.sketch().segment((-75,-54),(-61,-62)).segment((-13,12)).segment((-27,21)).close().assemble().finalize().extrude(-104)).union(w1.sketch().arc((-100,-65),(-99,-59),(-100,-53)).close().assemble().finalize().extrude(-147))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00682175.step')
