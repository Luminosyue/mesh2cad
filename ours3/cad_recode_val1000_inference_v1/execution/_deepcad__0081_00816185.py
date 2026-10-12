import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-1))
r=w0.sketch().arc((-100,5),(-95,-9),(-81,-10)).segment((-81,-7)).segment((-77,-7)).segment((-77,-10)).arc((-67,-10),(-57,-7)).segment((-54,-7)).segment((-54,-4)).arc((-51,2),(-50,7)).segment((-54,7)).segment((-54,10)).segment((-57,10)).arc((-58,10),(-58,11)).arc((-79,10),(-100,5)).assemble().reset().face(w0.sketch().segment((-48,-4),(-29,-10)).segment((-29,-11)).segment((-27,-11)).segment((-27,-10)).segment((21,-10)).segment((21,-7)).segment((100,-10)).segment((100,8)).segment((21,11)).segment((21,12)).segment((19,12)).segment((19,11)).segment((-29,11)).segment((-29,7)).segment((-45,7)).close().assemble()).finalize().extrude(2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0081_00816185.step')
