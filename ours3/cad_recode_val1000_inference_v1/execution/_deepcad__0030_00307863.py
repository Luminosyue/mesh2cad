import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,25))
r=w0.sketch().segment((-100,-62),(-41,-62)).segment((-100,-6)).close().assemble().reset().face(w0.sketch().segment((-100,6),(-39,62)).segment((-100,62)).close().assemble()).reset().face(w0.sketch().segment((-10,-62),(100,-62)).segment((100,62)).segment((39,62)).segment((10,62)).segment((10,17)).segment((61,17)).segment((61,-17)).segment((10,-17)).segment((10,-62)).close().assemble()).finalize().extrude(-50).union(w0.sketch().segment((-88,-18),(-74,-18)).arc((-48,-33),(-22,-18)).segment((88,-18)).segment((88,18)).segment((-22,18)).arc((-48,33),(-74,18)).segment((-88,18)).close().assemble().finalize().extrude(-3))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00307863.step')
