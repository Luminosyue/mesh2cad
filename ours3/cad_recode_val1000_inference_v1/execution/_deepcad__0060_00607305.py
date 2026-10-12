import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,83))
w1=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-100,-67),(88,-67)).segment((88,-56)).segment((100,-56)).segment((100,67)).segment((-96,66)).segment((-96,58)).segment((-100,58)).close().assemble().push([(6.5,0)]).rect(179,74,mode='s').finalize().extrude(-166).union(w0.sketch().segment((-91,30),(91,30)).segment((91,64)).segment((27,64)).arc((25,62),(23,64)).segment((-61,64)).arc((-75,37),(-91,64)).close().assemble().finalize().extrude(-73)).union(w1.sketch().segment((-37,50),(-37,83)).arc((-19,-76),(64,50)).close().assemble().finalize().extrude(-177))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0060_00607305.step')
