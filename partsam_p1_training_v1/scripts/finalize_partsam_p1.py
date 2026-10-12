from pathlib import Path
import sys,os,json,ast,re,hashlib,collections,copy
os.environ['OMP_NUM_THREADS']='1'
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');OUT=ROOT/'partsam_p1_training_v1'
sys.path[:0]=[str(OUT/'scripts'),str(ROOT),str(ROOT/'scripts'),str(ROOT/'SpatialLM')]
import numpy as np,torch
torch.set_num_threads(2)
OPS={'Box','Cylinder','Circle','Sketch','Extrude','ExtrudePolygon','Union','Cut','Revolve','PolygonProfile','Axis','TrueRevolve','Fillet','Chamfer'}
MODEL=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1'

def dump(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False,default=str),encoding='utf-8')
def jsonl(p,rows):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def asthash(text):return hashlib.sha256(ast.dump(ast.parse(text),include_attributes=False).encode()).hexdigest()

def mask_row(cad_id,text,tok):
    enc=tok(text,add_special_tokens=False,return_offsets_mapping=True);ids=enc['input_ids'];offsets=enc['offset_mapping'];hits=[]
    truth=collections.Counter(n.func.id for n in ast.walk(ast.parse(text)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in OPS)
    for op in sorted(OPS,key=len,reverse=True):
        spans=[m.span(1) for m in re.finditer(r'(?<![A-Za-z0-9_])('+op+r')\s*\(',text)]
        assert len(spans)==truth[op]
        for cs,ce in spans:
            ix=[j for j,(a,b) in enumerate(offsets) if b>cs and a<ce];assert ix
            hits.append({'operation':op,'char_span':[cs,ce],'token_indices':ix,'token_ids':[ids[i] for i in ix]})
    hits.sort(key=lambda x:x['token_indices'][0]);assert hits
    return {'cad_id':cad_id,'response_sha256':hashlib.sha256(text.encode()).hexdigest(),'response_token_ids':ids,
            'operations':[s['operation'] for s in hits],'operation_spans':hits}

def main():
    from transformers import AutoTokenizer
    from spatiallm_curve_token_c2_frozen_v2.export_curve_tokens import curve_inputs,load_backbone,DEFAULT_CKPT
    from spatiallm_curve_token_v1 import curve_token_injector as ci
    checkpoint_hash=sha(DEFAULT_CKPT)
    assert checkpoint_hash=='553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9'
    model,_=load_backbone(DEFAULT_CKPT,torch.device('cpu'))
    tok=AutoTokenizer.from_pretrained(MODEL,use_fast=True,local_files_only=True)
    candidates=[];excluded=[];token_rows=[];dedup={};protected=set()
    # Exact AST overlap only. Geometric overlap with the legacy corpus is not claimed.
    for line in (ROOT/'ours3/exact9998_v1/EXACT9998_ASSET_REGISTRY_V1.jsonl').read_text().splitlines():
        legacy=json.loads(line)
        if legacy.get('split','').lower() in ('val','test'):
            protected.add(asthash(Path(legacy['target_path']).read_text()))
    records=json.loads((OUT/'geometry_results.json').read_text())
    geometry_ready_count=sum(r['status']=='geometry_ready' for r in records)
    for rec in records:
        if rec['status']!='geometry_ready':excluded.append(rec);continue
        dest=Path(rec['surface_path']).parent
        try:
            spec=json.loads((dest/'fitted_parameters_canonical.json').read_text())
            height=(spec['zmax']-spec['zmin']) if spec['kind']!='box' else float(np.min(np.array(spec['maxs'])-np.array(spec['mins'])))
            if height/6<1e-4:raise ValueError('near_planar_unresolved_thickness_below_1e-4_diagonal')
            import cadquery as cq
            solid=cq.importers.importStep(str(dest/'model.step')).val()
            thickness=2*solid.Volume()/solid.Area()/6
            rec['effective_thickness_diagonal_ratio']=thickness
            if thickness<1e-4:raise ValueError('near_planar_effective_thickness_below_1e-4_diagonal')
            text=(dest/'program_canonical.dsl').read_text();targethash=asthash(text)
            if targethash in protected:raise ValueError('protected_eval_exact_target_overlap')
            if targethash in dedup:
                rec['duplicate_of']=dedup[targethash];raise ValueError('duplicate_canonical_target')
            z=np.load(dest/'curve_samples.npz');kept=np.load(dest/'selected_curve_indices.npy')
            feats,scales=zip(*(curve_inputs(z['curve_xyz_normalized'][i].astype(np.float64),z['curve_tangent'][i]) for i in kept))
            feats=np.stack(feats);scales=np.stack(scales)
            with torch.inference_mode():tokens=model(torch.from_numpy(feats),torch.from_numpy(scales))['token'].float().numpy()
            assert tokens.shape==(len(kept),256) and np.isfinite(tokens).all() and 1<=len(kept)<=128
            np.savez_compressed(dest/'encoder_input_c2.npz',feats=feats,scale_feat=scales,edge_id=z['curve_edge_id'][kept],selection_index=kept)
            tokenpath=dest/'curve_tokens.npy';np.save(tokenpath,tokens)
            rec.update(curve_token_path=str(tokenpath),curve_token_shape=list(tokens.shape),c2_checkpoint_sha256=checkpoint_hash,
                       target_sha256=sha(dest/'program_canonical.dsl'),mask=mask_row(rec['cad_id'],text,tok),status='assets_ready')
            prompt='<point_cloud>\nGenerate CAD construction program from the point cloud.\n\nAllowed operations (CAD DSL v1):\nBox, Cylinder, ExtrudePolygon, Cut, Union\n\nOutput only valid DSL assignments ending with result = ...'
            rec['example']={'id':rec['cad_id'],'dataset':'partsam','sample_id':rec['sample_id'],
                'conversations':[{'from':'human','value':prompt},{'from':'gpt','value':text}], 'point_clouds':[rec['surface_path']]}
            candidates.append(rec);dedup[targethash]=rec['cad_id']
            token_rows.append({'cad_id':rec['cad_id'],'dataset':'partsam','sample_id':rec['sample_id'],
                'curve_token_path':str(tokenpath),'curve_token_sha256':sha(tokenpath),'shape':list(tokens.shape),
                'c2_checkpoint_path':str(DEFAULT_CKPT),'c2_checkpoint_sha256':checkpoint_hash})
        except Exception as e:
            rec.update(status='excluded',reason=str(e));excluded.append(rec)
    jsonl(OUT/'CURVE_TOKEN_REGISTRY.jsonl',token_rows)
    # Runtime needs a registry before invoking the real P1 collator.
    jsonl(OUT/'masks/TRAIN_OPERATION_TOKEN_MASK_REGISTRY.jsonl',[r['mask'] for r in candidates]);jsonl(OUT/'masks/VAL_OPERATION_TOKEN_MASK_REGISTRY.jsonl',[])
    from partsam_p1_runtime import install
    install()
    from spatiallm.tuner.data.template import register_spatiallm_templates,get_template_and_fix_tokenizer
    from spatiallm.tuner.hparams import DataArguments
    from spatiallm.tuner.data.collator import MultiModalDataCollatorForSeq2Seq
    import p1_operation_loss_runtime as op
    register_spatiallm_templates(cutoff_len=8192,num_bins=1280,do_augmentation=False,random_rotation=False)
    template=get_template_and_fix_tokenizer(tok,DataArguments(template='spatiallm_cad_llama_sepedge'))
    collator=MultiModalDataCollatorForSeq2Seq(tokenizer=tok,template=template,model=None)
    accepted=[];collator_audits=[]
    for rec in candidates:
        try:
            example=rec['example'];text=example['conversations'][1]['value']
            feature={'_prompt':[{'role':'user','content':example['conversations'][0]['value']}],
                     '_response':[{'role':'assistant','content':text}], '_point_clouds':example['point_clouds'],'_system':''}
            np.random.seed(20260919)
            batch=collator([copy.deepcopy(feature)])
            ids=batch['input_ids'][0].tolist();labels=batch['labels'][0].tolist();supervised=[x for x in labels if x!=-100]
            response_ids=rec['mask']['response_token_ids']
            # Require complete target sequence, not merely nonempty labels.
            start=op.locate(ids,response_ids,valid=[v!=-100 for v in labels]);assert start>=0,'target_truncated_or_tokenizer_mismatch'
            assert labels[-1]==tok.eos_token_id,'EOS_not_supervised'
            assert int(batch['operation_mask'].sum())>0
            assert not bool((batch['operation_mask'] & (batch['labels']==-100)).any())
            # Conservative upper bound: <= one surface token per retained voxel.
            # No assumption about Sonata's reduction ratio is needed.
            surface_n=int(batch['point_clouds'].shape[1]);curve_n=int(batch['edge_clouds'].shape[1])
            budget=len(ids)+surface_n+curve_n
            assert budget<=8192,f'conservative_context_bound:{budget}'
            loaded=ci.load_curve_tokens(Path(rec['surface_path']));assert loaded.shape==tuple(rec['curve_token_shape'])
            audit={'cad_id':rec['cad_id'],'text_length':len(ids),'supervised_tokens':len(supervised),'operation_mask_tokens':int(batch['operation_mask'].sum()),
                   'surface_voxels':surface_n,'curve_tokens':curve_n,'conservative_context_upper_bound':budget,
                   'TARGET_TRUNCATED':False,'EOS_SUPERVISED':True,'RESULT_SUPERVISED':True,'LABEL_MASK_VALID':True,'status':'PASS'}
            rec['collator_audit']=audit;collator_audits.append(audit);accepted.append(rec)
        except Exception as e:
            rec.update(status='excluded',reason='runtime_audit:'+str(e));excluded.append(rec)
    # Keep all siblings in one split. Hash split is deterministic and never tuned to a score.
    # Also group near-identical scalar CAD signatures conservatively across objects.
    import cadquery as cq
    parent={r['object_id']:r['object_id'] for r in accepted}
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    signatures={}
    for rec in accepted:
        shape=cq.importers.importStep(rec['step_path']).val();bb=shape.BoundingBox();di=(bb.xlen**2+bb.ylen**2+bb.zlen**2)**.5
        signature=(tuple(round(v/di,3) for v in sorted([bb.xlen,bb.ylen,bb.zlen])),round(shape.Volume()/di**3,4),round(shape.Area()/di**2,4),
                   tuple(sorted((e.geomType(),round(e.Length()/di,3)) for e in shape.Edges())))
        if signature in signatures:
            a,b=find(rec['object_id']),find(signatures[signature]);parent[max(a,b)]=min(a,b)
        else:signatures[signature]=rec['object_id']
        rec['geometry_group_signature']=hashlib.sha256(repr(signature).encode()).hexdigest()
    groups=sorted(set(find(r['object_id']) for r in accepted),key=lambda x:hashlib.sha256(('partsam_p1_v1:'+x).encode()).hexdigest())
    # Exact group counts near 80/10/10; if too few groups, retain training only.
    nval=max(1,round(len(groups)*.1)) if len(groups)>=10 else 0
    ntest=nval
    splits={g:('val' if i<nval else 'test' if i<nval+ntest else 'train') for i,g in enumerate(groups)}
    dataset_info={};asset_rows=[]
    for split in ('train','val','test'):
        subset=[r for r in accepted if splits[find(r['object_id'])]==split]
        dump(OUT/f'partsam_p1_{split}.json',[r['example'] for r in subset])
        jsonl(OUT/'masks'/f'{split.upper()}_OPERATION_TOKEN_MASK_REGISTRY.jsonl',[r['mask'] for r in subset])
        dataset_info[f'partsam_p1_{split}']={'file_name':f'partsam_p1_{split}.json','formatting':'sharegpt','columns':{'messages':'conversations','point_clouds':'point_clouds'}}
        for r in subset:
            r.update(split=split,split_group=find(r['object_id']),status='training_ready',standalone_training_ready=True,
                     legacy_exact9998_mixing_approved=False,legacy_geometry_overlap_audit='NOT_RUN; exact target overlap checked only')
            record={k:v for k,v in r.items() if k not in ('mask','example')};asset_rows.append(record)
            dump(Path(r['surface_path']).parent/'training_record.json',record)
    dump(OUT/'dataset_info.json',dataset_info);jsonl(OUT/'ASSET_REGISTRY.jsonl',asset_rows)
    jsonl(OUT/'EXCLUDED.jsonl',[{k:v for k,v in r.items() if k not in ('mask','example','traceback')} for r in excluded])
    dump(OUT/'audits/COLLATOR_AUDIT.json',collator_audits)
    # Token registry is reduced to the final eligible cohort; no silent missing-asset fallback.
    ids={r['cad_id'] for r in accepted};jsonl(OUT/'CURVE_TOKEN_REGISTRY.jsonl',[r for r in token_rows if r['cad_id'] in ids])
    assert sha(DEFAULT_CKPT)==checkpoint_hash
    summary={'input_count':len(records),'geometry_ready_before_training_gates':geometry_ready_count,
             'training_ready_count':len(accepted),'excluded_count':len(excluded),'split_counts':dict(collections.Counter(r['split'] for r in accepted)),
             'object_count':len(parent),'split_group_count':len(groups),'exclusion_reasons':dict(collections.Counter(r.get('reason','unknown') for r in excluded)),
             'geometry_classes':dict(collections.Counter(r['geometry_class'] for r in accepted)),
             'operation_counts':dict(collections.Counter(o for r in accepted for o in r['mask']['operations'])),
             'checkpoint_sha256':checkpoint_hash,'collator_audit_pass_count':len(collator_audits),
             'training_started':False,'source':'original specified STL; no mismatched same-ID upstream CAD reused',
             'provenance':'reconstructed CAD pseudo supervision','legacy_dataset_unchanged':True,
             'legacy_mixing_requires_geometric_overlap_audit':True,'minimum_resolved_thickness_diagonal_ratio':1e-4,
             'validation_scope':'actual CPU P1 data collator, masks and conservative context bound; no model forward/backward or optimization'}
    dump(OUT/'FINAL_SUMMARY.json',summary)
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
