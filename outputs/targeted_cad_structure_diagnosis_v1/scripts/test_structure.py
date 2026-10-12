from structure_common import *
from residual_features import *
import cadquery as cq
from validate_native_parametric_cad import code_audit
from semantic_feature_review import check as semantic_check
def test():
 checks=[]
 origin=np.zeros(3);pitch=1/64;idx=np.indices((64,64,64)).reshape(3,-1).T;points=idx*pitch;cube=np.all((points>.1)&(points<.9),axis=1).reshape(64,64,64)
 for kind,operation in [('CYLINDER','cut'),('SLOT','cut'),('BOX','union')]:
  p={'shape':kind,'operation':operation,'center':[.5,.5,.5] if operation=='cut' else [.89,.5,.5],'basis':np.eye(3).tolist(),'dimensions':[.24,.24,.85] if kind=='CYLINDER' else [.5,.15,.85] if kind=='SLOT' else [.18,.25,.25]}
  mask=inside(points,p).reshape(cube.shape);source=(cube&~mask) if operation=='cut' else (cube|mask);q=optimize_feature(p,source,cube,origin,pitch);assert q['rule_verified'] and q['proxy_iou']>.97,(kind,q);code='import cadquery as cq\nresult = cq.Workplane("XY").box(1.0,1.0,1.0)\n'+emit(q,1);assert code_audit(code)['safe_grammar'];scope={};exec(code,scope);assert scope['result'].val().isValid()
  dummy=trimesh.creation.box(extents=[.8,.8,.8]);dummy.apply_translation([.5,.5,.5]);residual=(cube&~source) if operation=='cut' else (source&~cube);cs,labels=components(residual,origin,pitch,dummy,dummy);assert sum(c['voxel_n'] for c in cs)==int(residual.sum());fits=fit_component(cs[0],labels,'EXTRA' if operation=='cut' else 'MISSING',source,cube,origin,pitch,'import cadquery as cq\nresult = cq.Workplane("XY").box(1.0,1.0,1.0)\n');fitted=[optimize_feature(f,source,cube,origin,pitch) for f in fits];assert fitted and max(x['proxy_iou'] for x in fitted)>.97,(kind,[(x['shape'],x['proxy_iou']) for x in fitted]);assert semantic_check(q,{'source':source,'origin':origin,'pitch':pitch})['semantic_rule_supported'];checks.append(kind+'_'+operation+'_extraction_fit_optimize_native_semantic')
 endtrim={'shape':'BOX','operation':'cut','feature_type':'RECESS','center':[.5,.5,.88],'basis':np.eye(3).tolist(),'dimensions':[.85,.85,.12]};trimmed=cube&~inside(points,endtrim).reshape(cube.shape);assert semantic_check(endtrim,{'source':trimmed,'origin':origin,'pitch':pitch})['semantic_feature_type']=='GENERIC_CUT_OR_END_TRIM';checks.append('end_trim_not_mislabeled_as_pocket')
 # Actual data evaluator source sample cache shape and deterministic equivalence.
 row=read(O/'manifests/subset.json')[0];d=O/'cases'/row['case_id'];m=trimesh.load(d/'source/part_local.ply',force='mesh',process=True);frozen=np.load(d/'source/frozen_evaluation_points.npy');exact,_=trimesh.sample.sample_surface(m,20000,seed=row['seed']);print('FROZEN_SHAPE',frozen.shape,'EVAL_SHAPE',exact.shape,flush=True)
 np.save(d/'source/evaluation_source_points.npy',exact)
 dump(O/'integrity/DETECTOR_TESTS.json',{'pass':True,'synthetic_cases':checks,'source_frozen_shape':list(frozen.shape),'evaluator_source_shape':list(exact.shape),'existing_cache_equals_evaluator':bool(frozen.shape==exact.shape and np.array_equal(frozen,exact))})
 print('DETECTOR_TESTS_PASS',checks,flush=True)
if __name__=='__main__':test()
