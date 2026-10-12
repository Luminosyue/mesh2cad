"""Adversarial grammar tests and real OCC positive/negative controls."""
from validate_native_parametric_cad import *
O=Path(__file__).resolve().parents[1]/'tests';O.mkdir(exist_ok=True)
tests=[]
cases={
 'native_box':('import cadquery as cq\nresult=cq.Workplane("XY").box(1,2,3)\n',True),
 'native_cylinder':('import cadquery as cq\nresult=cq.Workplane("XY").circle(1).extrude(2)\n',True),
 'native_triangle_prism':('import cadquery as cq\nresult=cq.Workplane("XY").polyline([[0,0],[1,0],[0,1]]).close().extrude(2)\n',True),
 'native_loft':('import cadquery as cq\nresult=cq.Workplane("XY").circle(1).workplane(offset=1).rect(1,1).loft()\n',True),
 'mesh_import':('import cadquery as cq\nresult=cq.importers.importStl("source.stl")\n',False),
 'vertex_face_arrays':('import cadquery as cq\nvertices=[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]]\nfaces=[[0,1,2]]\nresult=cq.Face.makeFromWires(cq.Wire.makePolygon(vertices))\n',False),
 'renamed_triangle_soup':('import cadquery as cq\na=[[0,0,0],[1,0,0],[0,1,0]]\nb=cq.Wire.makePolygon(a)\nresult=cq.Face.makeFromWires(b)\n',False),
 'import_alias':('import cadquery as cq\nimport trimesh as innocent\nresult=innocent.load("part.obj")\n',False),
 'decoy_feature':('import cadquery as cq\ndecoy=cq.Workplane("XY").box(1,1,1)\nresult=cq.Workplane("XY")\n',False),
 'external_step':('import cadquery as cq\nresult=cq.importers.importStep("old.step")\n',False),
 'getattr_bypass':('import cadquery as cq\nresult=getattr(cq,"importers").importStep("x.step")\n',False),
 'eval_bypass':('import cadquery as cq\nresult=eval("1")\n',False),
 'numpy_payload':('import cadquery as cq\nimport numpy as np\nresult=cq.Workplane("XY").polyline(np.load("vertices.npy")).close().extrude(1)\n',False),
 'loop_shell':('import cadquery as cq\nfor tri in triangles:\n face=cq.Face.makeFromWires(cq.Wire.makePolygon(tri))\nresult=cq.Shell.makeShell(faces)\n',False),
 'nonfinite':('import cadquery as cq\nresult=cq.Workplane("XY").box(1e999,1,1)\n',False),
 'cq_reassignment':('import cadquery as cq\ncq=cq.Workplane("XY")\nresult=cq.box(1,1,1)\n',False),
}
for name,(code,expected) in cases.items():
 r=code_audit(code);passed=r['safe_grammar']==expected;tests.append({'name':name,'expected_safe':expected,'actual_safe':r['safe_grammar'],'pass':passed,'reasons':r['unsupported_reasons']})
 if expected:
  d=O/name;d.mkdir(exist_ok=True);(d/'cad.py').write_text(code);scope={};exec(code,scope);shape=scope['result'].val();cq.exporters.export(shape,str(d/'cad.step'));v,f=shape.tessellate(.01,.1);trimesh.Trimesh([x.toTuple() for x in v],f).export(d/'source.ply');full=validate(d/'cad.py',d/'cad.step',d/'source.ply',d/'run');dump(d/'audit.json',full);tests.append({'name':name+'_end_to_end','classification':full['classification'],'pass':full['classification']=='A_NATIVE_PARAMETRIC'})
# Analytic ratios alone must not accept a triangulated B-Rep.
d=O/'faceted_positive_control';d.mkdir(exist_ok=True);m=trimesh.creation.icosphere(subdivisions=2);m.export(d/'source.ply');fs=[]
for indices in m.faces:
 wire=cq.Wire.makePolygon([cq.Vector(*p) for p in m.vertices[indices]],close=True);fs.append(cq.Face.makeFromWires(wire))
shape=cq.Compound.makeCompound(fs);cq.exporters.export(shape,str(d/'cad.step'))
code='import cadquery as cq\nvertices='+repr(m.vertices.tolist())+'\nfaces='+repr(m.faces.tolist())+'\nresult=cq.Compound.makeCompound([cq.Face.makeFromWires(cq.Wire.makePolygon([vertices[i] for i in tri],close=True)) for tri in faces])\n';(d/'cad.py').write_text(code)
r=validate(d/'cad.py',d/'cad.step',d/'source.ply',d/'run');dump(d/'audit.json',r);tests.append({'name':'faceted_positive_control','classification':r['classification'],'triangle_ratio':r['triangle_planar_face_ratio'],'compression_ratio':r['compression_ratio'],'pass':r['classification']=='D_MESH_WRAPPER' and r['triangle_planar_face_ratio']==1 and not r['accepted_for_parametric_dataset']})
# A native decoy program must not legitimize an unrelated STEP.
d2=O/'mismatched_code_step';d2.mkdir(exist_ok=True);(d2/'cad.py').write_text(cases['native_box'][0]);r2=validate(d2/'cad.py',O/'native_cylinder/cad.step',O/'native_cylinder/source.ply',d2/'run');dump(d2/'audit.json',r2);tests.append({'name':'mismatched_code_step','classification':r2['classification'],'pass':not r2['accepted_for_parametric_dataset']})
dump(O/'TEST_RESULTS.json',{'pass':all(t['pass'] for t in tests),'test_n':len(tests),'tests':tests});print(json.dumps(tests,indent=2));assert all(t['pass'] for t in tests)
