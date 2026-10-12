import collections, hashlib, json, pathlib
import numpy as np

ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'cad_spatial_dataset/geometry_pack_v2_practical/_audit_stage1_v2'
rows=json.loads((OUT/'inventory.json').read_text()); result=[]
for r in rows:
    p=pathlib.Path(r['pack']); tf=json.loads((p/'coordinate_transform.json').read_text())
    s=float(tf['scale']); t=np.array(tf['translation']); a=np.load(p/'surface_points.npy'); raw=np.load(p/'surface_points_source.npy')
    diag=float(tf['source_diagonal']); canon_d=diag*s
    rec={'cad_id':r['cad_id'],'dataset':r['dataset'],'surface_shape':list(a.shape),'surface_affine_max_error_rel':float(np.abs(a[:,:3]-(raw*s+t)).max()/canon_d),'surface_normal_unit_max_error':float(np.abs(np.linalg.norm(a[:,3:6],axis=1)-1).max()),'sample_bbox_diag_to_transform_source_diag':float(np.linalg.norm(raw.max(0)-raw.min(0))/diag)}
    edge=np.load(p/'edge_points_detected.npy'); norms=np.linalg.norm(edge[:,3:6],axis=1)
    rec.update(edge_points=len(edge),edge_nonunit_normals=int((np.abs(norms-1)>1e-4).sum()),edge_zero_normals=int((norms<1e-10).sum()))
    cp=ROOT/'ours3/curve_token_data_v1'/('deepcad_train' if r['dataset']=='deepcad' else 'fusion360_train')/r['sample_id']
    try:
        nz=json.loads((cp/'normalization.json').read_text()); z=np.load(cp/'curve_samples.npz'); mask=z['curve_mask'].astype(bool)
        rec['curve_transform_matches_surface']=bool(abs(float(nz['scale'])-s)<1e-10 and np.allclose(nz['translation'],t,atol=1e-10,rtol=0))
        xyz=z['curve_xyz'].astype('float64'); transformed=z['curve_xyz_normalized'].astype('float64')
        rec['curve_affine_max_error_rel']=float(np.abs(transformed[mask]-(xyz*s+t)[mask]).max()/canon_d) if mask.any() else None
        tang=z['curve_tangent'][mask]; tn=np.linalg.norm(tang,axis=1)
        rec['curve_nonunit_valid_tangents']=int((np.abs(tn-1)>1e-4).sum())
        lens=z['curve_length'].astype('float64'); ln=z['curve_length_normalized'].astype('float64')
        rec['curve_length_affine_max_error_rel']=float(np.max(np.abs(ln-lens*s))/canon_d) if len(lens) else 0
        rec['raw_curve_count']=int(z['num_curves'][0]); rec['nonline_curve_count']=int((z['curve_type_id']!=0).sum())
    except Exception as e:rec['curve_error']=repr(e)
    result.append(rec)
    if len(result)%500==0: print('protocol_checked',len(result),flush=True)
summary={'n':len(result),'source':{},'definition':'Numerical checks in stored V1, not a new normalization or a V2 acceptance gate. Surface raw and normalized arrays compared with the frozen affine map; tangent unit tolerance 1e-4 on valid curve mask; normal unit tolerance 1e-4. No rotation introduced.','limitations':['Edge raw-point correspondences are not independently reconstructed here.','The C2 local-shape encoder additionally centers/scales each curve; shared object transform does not mean global curve centroid is retained in its tokens.','Transform-source bbox ratio is diagnostic; tessellation/sampling may produce small differences. A factor of ten is not explained by sampling.'],'new_training_started':False,'test_model_metrics_read':False}
for ds in ('deepcad','fusion360'):
    rr=[x for x in result if x['dataset']==ds]
    summary['source'][ds]={'n':len(rr),'curve_transform_mismatch':sum(x.get('curve_transform_matches_surface') is False for x in rr),'surface_shape_fail':sum(x['surface_shape']!=[8192,6] for x in rr),'curve_errors':sum('curve_error' in x for x in rr),'surface_affine_fail_gt_1e_5':sum(x['surface_affine_max_error_rel']>1e-5 for x in rr),'sample_bbox_ratio_gt_1_1':sum(x['sample_bbox_diag_to_transform_source_diag']>1.1 for x in rr),'sample_bbox_ratio_near10':sum(abs(x['sample_bbox_diag_to_transform_source_diag']-10)<.1 for x in rr),'surface_nonunit_rows':sum(x['surface_normal_unit_max_error']>1e-4 for x in rr),'edge_nonunit_rows':sum(x['edge_nonunit_normals']>0 for x in rr),'curve_nonunit_rows':sum(x.get('curve_nonunit_valid_tangents',0)>0 for x in rr),'curves_gt128_rows':sum(x.get('raw_curve_count',0)>128 for x in rr)}
for name,obj in [('NORMALIZATION_SUMMARY.json',summary),('NORMALIZATION_ROWS.json',result)]:
    with (OUT/'reports'/name).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False)
print(json.dumps(summary,indent=2))
