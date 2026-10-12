from profile_native import *
from native_geometry import param_transform
from validate_native_parametric_cad import code_audit,validate as native_validate
import cadquery as cq,trimesh
T=O/'tests';T.mkdir(exist_ok=True);results=[]
theta=np.linspace(0,2*np.pi,80,endpoint=False)
samples={'circle':np.c_[np.cos(theta),np.sin(theta)],'ellipse':np.c_[2*np.cos(theta),np.sin(theta)],'smooth_freeform':np.c_[(1+.13*np.cos(3*theta))*np.cos(theta),(1+.13*np.cos(3*theta))*np.sin(theta)],'spline_kernel_control':np.c_[(1+.1*np.cos(3*theta))*np.cos(theta),(1+.1*np.cos(3*theta))*np.sin(theta)]}
rr={'type':'ROUNDED_RECT','center':[0.,0.],'half_extents':[1.,.6],'orientation':.2,'radius':.2}
for name,pts in samples.items():
 rec=recognize(pts,20261007);rep={'type':'BSPLINE'} if name=='spline_kernel_control' else choose(rec,'analytic' if name!='smooth_freeform' else 'spline');d=T/name;d.mkdir(exist_ok=True);code='import cadquery as cq\nplane=cq.Plane(origin=[0.,0.,0.],xDir=[1.,0.,0.],normal=[0.,0.,1.])\nresult='+profile_expression('cq.Workplane(plane)',pts,rep)+'.extrude(0.8)\n';(d/'cad.py').write_text(code);scope={};exec(code,scope);shape=scope['result'].val();cq.exporters.export(shape,str(d/'cad.step'));vv,ff=shape.tessellate(.001,.05);m=trimesh.Trimesh([v.toTuple() for v in vv],ff);m.export(d/'source.ply');audit=native_validate(d/'cad.py',d/'cad.step',d/'source.ply',d/'validation');dump(d/'audit.json',audit);assert audit['classification']=='A_NATIVE_PARAMETRIC',(name,audit['reasons']);results.append({'name':name,'selected_type':rep['type'],'representation':'A_NATIVE_PARAMETRIC'})
 x=np.array([.02,-.01,.005,-.004,.003,.002,.001,-.002]);changed,A,b=param_transform(code,x,m.bounds.mean(0),True);scope2={};exec(changed,scope2);s2=scope2['result'].val();pred_volume=shape.Volume(tol=1e-10)*abs(np.linalg.det(A));err=abs(s2.Volume(tol=1e-10)-pred_volume)/max(pred_volume,1e-12);assert err<1e-6,(name,err);results[-1]['parameter_rewrite_volume_error']=err;results[-1]['volume_integration_tolerance']=1e-10
expr=profile_expression('cq.Workplane("XY")',samples['circle'],rr);scope={};exec('import cadquery as cq\nresult='+expr+'.extrude(1)',scope);shape=scope['result'].val();expected=4*1*.6-(4-np.pi)*.2**2;assert abs(shape.Volume()-expected)<1e-8;results.append({'name':'rounded_rectangle_line_arc','volume_error':abs(shape.Volume()-expected)})
for code in ['import cadquery as cq\nresult=cq.importers.importStl("x.stl")','import cadquery as cq\nresult=cq.Workplane("XY").spline('+repr(np.c_[np.cos(theta),np.sin(theta)].tolist())+',periodic=True).extrude(1)']:
 assert not code_audit(code)['safe_grammar'];results.append({'name':'unsupported_import_or_excess_spline_blocked','pass':True})
dump(T/'PROFILE_TEST_RESULTS.json',{'pass':True,'test_n':len(results),'results':results,'synthetic_tests_only_not_dataset_examples':True});print(results)
