"""Export the initial smooth tire CAD using the repository's exact P1/C2 recipe.

This script reads repository implementations and checkpoints, and writes only to
this isolated example directory. It does not modify training datasets or weights.
"""
from pathlib import Path
import sys,json,hashlib,copy,collections
import numpy as np
import torch

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from curve_token_v1.extract_brep_curves import extract_curves_from_shape
from curve_token_v1.canonicalize_curves import resolve_normalization,canonicalize_curves
from curve_token_v1.occ_curve_v1 import load_step_shape,make_adaptor
from curve_token_v1.extract_topology import extract_topology,topology_arrays
from curve_token_v1.sample_curves import build_sample_arrays
from curve_encoder_baseline_v1.dataset import _normalized_s,_pack_params
from curve_encoder_baseline_v1.models import build_model as build_p1_model
from curve_encoder_baseline_v1.config import EXPERIMENTS as P1_EXPERIMENTS
from spatiallm_curve_token_c2_frozen_v2.export_curve_tokens import curve_inputs,load_backbone,DEFAULT_CKPT,MAX_CURVE_TOKENS
from geometry_pack_v1.occ import extract_brep_edges
from geometry_pack_v1.constants import SHARP_ANGLE_DEG
from OCP.BRep import BRep_Tool
from OCP.TopAbs import TopAbs_EDGE,TopAbs_FACE
from OCP.TopExp import TopExp
from OCP.TopoDS import TopoDS
from OCP.TopTools import TopTools_IndexedMapOfShape

def dump(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,default=lambda v:v.tolist() if isinstance(v,np.ndarray) else str(v)),encoding='utf-8')

def main():
    torch.set_num_threads(2)
    source=OUT/'source/part_006_smooth.step'
    shape=load_step_shape(source)
    data=extract_curves_from_shape(shape,cad_id='tire_part006_smooth')
    nz=resolve_normalization(None,data['source_bbox_min'],data['source_bbox_max'])
    data=canonicalize_curves(data,nz)
    records=data['curves']
    emap=TopTools_IndexedMapOfShape();TopExp.MapShapes_s(shape,TopAbs_EDGE,emap)
    fmap=TopTools_IndexedMapOfShape();TopExp.MapShapes_s(shape,TopAbs_FACE,fmap)
    adaptors=[make_adaptor(TopoDS.Edge_s(emap.FindKey(r['edge_id']+1))) for r in records]
    topology=extract_topology(shape,records)
    arrays=build_sample_arrays(adaptors,records,32,nz)
    arrays.update(topology_arrays(topology,records))
    brep=extract_brep_edges(shape,data['source_diagonal'])
    sharp_by_id={r['edge_index']:r['dihedral_deg']>SHARP_ANGLE_DEG for r in brep['edges']}
    dihedral_by_id={r['edge_index']:r['dihedral_deg'] for r in brep['edges']}
    for rec in records:
        edge=TopoDS.Edge_s(emap.FindKey(rec['edge_id']+1))
        rec['is_seam']=any(BRep_Tool.IsClosed_s(edge,TopoDS.Face_s(fmap.FindKey(i+1))) for i in rec['face_ids'])
        rec['dihedral_deg']=dihedral_by_id.get(rec['edge_id'],0.)
        rec['is_sharp']=sharp_by_id.get(rec['edge_id'],False)
        rec['sharp_angle_threshold_deg']=SHARP_ANGLE_DEG
        rec['provenance']='B-Rep edge of fitted smooth tire CAD; not measured ground truth or a triangle-mesh edge'
    np.savez_compressed(OUT/'curve_samples.npz',**arrays)
    dump('curves.json',data);dump('topology.json',topology)
    dump('normalization.json',nz.to_json())
    dump('coordinate_transform.json',nz.to_json())
    dense=build_sample_arrays(adaptors,copy.deepcopy(records),256,nz)
    np.savez_compressed(OUT/'curve_samples_256.npz',**dense)

    xyz=arrays['curve_xyz_normalized'].astype(np.float32)
    tangent=arrays['curve_tangent'].astype(np.float32)
    s=np.stack([_normalized_s(x,m) for x,m in zip(xyz,arrays['sampling_mode'])])
    p1=np.concatenate([xyz,tangent],axis=-1).astype(np.float32)
    packed=[_pack_params(r['curve_type'],r['normalized_parameters']) for r in records]
    params=np.stack([p[0] for p in packed]);param_mask=np.stack([p[1] for p in packed])
    sharp=np.array([r['is_sharp'] for r in records],dtype=bool)
    seam=np.array([r['is_seam'] for r in records],dtype=bool)
    np.savez_compressed(OUT/'encoder_input_p1.npz',feats=p1,xyz=xyz,tangent=tangent,
                        s=s,point_mask=arrays['curve_mask'],edge_id=arrays['curve_edge_id'],
                        sharp_mask=sharp,seam_mask=seam)
    np.save(OUT/'p1_feats.npy',p1)
    torch.save({'feats':torch.from_numpy(p1),'edge_id':torch.from_numpy(arrays['curve_edge_id'])},OUT/'encoder_input_p1.pt')
    np.savez_compressed(OUT/'curve_labels.npz',type_id=arrays['curve_type_id'].astype(np.int64),param=params,param_mask=param_mask)
    np.savez_compressed(OUT/'baseline_cache_single_cad.npz',xyz=xyz,tangent=tangent,s=s,
                        type_id=arrays['curve_type_id'].astype(np.int64),param=params,param_mask=param_mask)

    p1ckpt=ROOT/'ours3/curve_encoder_baseline_v1/runs/P1_frozen_v1/best.pt'
    state=torch.load(p1ckpt,map_location='cpu',weights_only=False)
    model=build_p1_model('pointnet',('xyz','tangent'))
    model.load_state_dict(state['model'],strict=True);model.eval()
    for p in model.parameters():p.requires_grad_(False)
    with torch.inference_mode():pred=model(torch.from_numpy(p1))
    tokens=pred['token'].float().numpy()
    np.save(OUT/'p1_curve_tokens.npy',tokens)
    np.save(OUT/'p1_predicted_type_id.npy',pred['type_logits'].argmax(-1).numpy())

    all_feats,all_scale=zip(*[curve_inputs(x.astype(np.float64),t) for x,t in zip(xyz,tangent)])
    all_feats=np.stack(all_feats);all_scale=np.stack(all_scale)
    poly_len=np.linalg.norm(np.diff(xyz.astype(np.float64),axis=1),axis=2).sum(axis=1)
    order=np.argsort(-poly_len)[:MAX_CURVE_TOKENS]
    sharp_order=np.array([i for i in np.argsort(-poly_len) if sharp[i]],dtype=np.int64)[:MAX_CURVE_TOKENS]
    c2model,c2state=load_backbone(DEFAULT_CKPT,torch.device('cpu'))
    for suffix,idx in [('all_edges',order),('sharp_only',sharp_order)]:
        f=all_feats[idx];sc=all_scale[idx]
        np.savez_compressed(OUT/f'encoder_input_c2_{suffix}.npz',feats=f,scale_feat=sc,edge_id=arrays['curve_edge_id'][idx],selection_index=idx)
        if len(idx):
            with torch.inference_mode():z=c2model(torch.from_numpy(f),torch.from_numpy(sc))['token'].float().numpy()
        else:z=np.empty((0,256),dtype=np.float32)
        np.save(OUT/f'c2_curve_tokens_{suffix}.npy',z)

    tangent_error=float(np.max(np.abs(np.linalg.norm(tangent,axis=2)-1)))
    assert arrays['curve_mask'].all()
    assert p1.shape==(len(records),32,6)
    assert np.isfinite(p1).all() and np.isfinite(tokens).all()
    assert tokens.shape==(len(records),256)
    assert tangent_error<1e-5
    assert all(r['extraction']['parameter_extraction_ok'] and r['extraction']['geometry_reconstruction_ok'] for r in records)
    inventory=[]
    for file in sorted(OUT.glob('*.npz')):
        with np.load(file) as z:inventory.append({'file':file.name,'arrays':{k:{'shape':list(z[k].shape),'dtype':str(z[k].dtype)} for k in z.files}})
    summary={'cad_source':str(source),'cad_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'num_curves':len(records),'curve_type_counts':dict(collections.Counter(r['curve_type'] for r in records)),
             'closed_curves':sum(r['is_closed'] for r in records),'seam_curves':int(seam.sum()),'sharp_curves':int(sharp.sum()),
             'sharp_angle_deg':SHARP_ANGLE_DEG,'p1_input_shape':list(p1.shape),'p1_output_shape':list(tokens.shape),
             'c2_all_edges_input_shape':list(all_feats[order].shape),'c2_sharp_only_input_shape':list(all_feats[sharp_order].shape),
             'all_parameter_extractions_pass':True,'all_parameter_reconstructions_pass':True,'all_samples_valid':True,
             'max_unit_tangent_error':tangent_error,'p1_checkpoint':str(p1ckpt),'p1_checkpoint_sha256':hashlib.sha256(p1ckpt.read_bytes()).hexdigest(),
             'c2_checkpoint':str(DEFAULT_CKPT),'c2_checkpoint_sha256':hashlib.sha256(DEFAULT_CKPT.read_bytes()).hexdigest(),
             'normalization_source':nz.source,'target_diagonal':nz.target_diagonal,
             'actual_operation_aware_p1_training_ready':False,
             'actual_p1_blockers':['zero sharp edges under the existing sharp-only C2 protocol','no validated canonical operation DSL target'],
             'p1_filename_namespace':'curve_encoder_baseline_v1 PointNet P1; not operation-aware LLM P1',
             'warning':'All-edge BREP seams and smooth patch joins are not physical sharp features; C2 all_edges is a diagnostic variant, not the sharp-only training selection.',
             'npz_inventory':inventory}
    dump('curve_export_summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='npz_inventory'},indent=2),flush=True)
    visualize(dense,records)

def visualize(dense,records):
    from PIL import Image,ImageDraw
    im=Image.new('RGB',(1800,1000),'#f5f7fb');draw=ImageDraw.Draw(im)
    pts=dense['curve_xyz'].astype(float);center=(pts.min((0,1))+pts.max((0,1)))/2
    span=float(np.ptp(pts.reshape(-1,3),axis=0).max())
    for col,direction in enumerate([np.array([1.,-1.,.8]),np.array([0.,0.,1.])]):
        zz=direction/np.linalg.norm(direction);xx=np.cross([0,0,1],zz) if abs(zz[2])<.99 else np.array([1.,0,0]);xx/=np.linalg.norm(xx);yy=np.cross(zz,xx)
        q=(pts-center)@np.array([xx,yy,zz]).T
        for i in np.argsort(q[:,:,2].mean(1)):
            rec=records[i];color='#e4802b' if rec['curve_type']=='BSPLINE' else '#157aa8'
            pix=q[i,:,:2]*[650/span,-650/span]+[450+col*900,530]
            draw.line([tuple(p) for p in pix],fill=color,width=3)
            if col==0:
                j=96 if rec['is_closed'] else 128
                draw.text(tuple(pix[j]),str(rec['edge_id']),fill='#29384a')
        draw.text((45+col*900,40),'Perspective' if col==0 else 'Top view',fill='#19324a',font_size=32)
    draw.text((45,100),'Blue: CIRCLE / arc     Orange: BSPLINE     Labels: edge_id',fill='#19324a',font_size=25)
    draw.text((45,940),'Curves extracted from the reconstructed smooth CAD; includes periodic seams and smooth patch boundaries.',fill='#19324a',font_size=20)
    im.save(OUT/'tire_curves_preview.png')

if __name__=='__main__':main()
