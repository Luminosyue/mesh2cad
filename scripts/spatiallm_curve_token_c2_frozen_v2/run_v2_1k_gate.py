#!/usr/bin/env python3
"""Build the canonical C2-corrected V2-1k dataset and probe the real LLM entry."""
from __future__ import annotations

import argparse, copy, hashlib, json, os, pathlib, sys, types
from collections import Counter

ROOT = pathlib.Path("/data/home/cuiyuehan/project/mesh2cad")
PHASE100 = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b1_budget_postencoder_phase1_v2_100/code"
sys.path[:0] = [str(PHASE100), str(ROOT / "SpatialLM"), str(ROOT / "scripts")]
os.environ.update(
    CAD_USE_SEPARATE_EDGE_TOKENS="1", CAD_SURFACE_POINTS="4096",
    CAD_HELDOUT_PROTOCOL="best_v2", CAD_EDGE_SOURCE="gt_sharp",
    CAD_EDGE_BUDGET_MATCH="0", CAD_SECOND_STREAM="edge_points",
    PYTHONDONTWRITEBYTECODE="1",
)

import numpy as np
import torch
from budget_matched import pack_stream, shared_k_valid, splice_geometry_masked
from spatiallm.model import spatiallm_llama as module
from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin
from spatiallm_curve_token_v1 import heldout_geometry
from spatiallm_curve_token_v1.curve_projector import build_curve_projector
from spatiallm_curve_token_v1.curve_token_injector import load_curve_tokens

K_CAP = 128
C2_ROOT = ROOT / "ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2"
C2_CKPT = ROOT / "ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt"
C2_CKPT_SHA256 = "553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9"
QUOTAS = {
    "deepcad": {"simple": 480, "medium": 160, "hard": 160},
    "fusion360": {"simple": 100, "medium": 50, "hard": 50},
}


class StopAtLlamaEntry(Exception): pass


def canonical_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def file_sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()


def difficulty(n): return "simple" if n <= 5 else ("medium" if n <= 10 else "hard")


def select_cohort():
    rows=json.loads((ROOT/"cad_spatial_dataset/geometry_pack_v2_practical/_audit_stage1_v2/reports/FULL_RESULTS.json").read_text())
    fpass=set(json.loads((ROOT/"cad_spatial_dataset/geometry_pack_v2_mesh2cad/placement_fix_retest_v3/STRICT_LABEL_PASS_CANDIDATES.json").read_text())["cad_ids"])
    keys=("source_identity","dsl_ast_sha256","geometry_fingerprint")
    nontrain={k:set(r.get(k) for r in rows if r.get("old_split")!="train" and r.get(k)) for k in keys}
    valid=[]; excluded_cross=0; excluded_missing=0
    for r in rows:
        if r.get("old_split")!="train": continue
        if not ((r["dataset"]=="deepcad" and r.get("label_gate")) or (r["dataset"]=="fusion360" and r["cad_id"] in fpass)): continue
        if any(r.get(k) in nontrain[k] for k in keys if r.get(k)):
            excluded_cross+=1; continue
        token=C2_ROOT/r["dataset"]/r["sample_id"]/"curve_tokens.npy"
        pack=pathlib.Path(r["pack"])
        if not (token.is_file() and (pack/"surface_points.npy").is_file() and (pack/"edge_points_gt_sharp.npy").is_file() and (pack/"cad_target.dsl").is_file()):
            excluded_missing+=1; continue
        valid.append(r)
    chosen=[]; used={k:set() for k in keys}
    pool_counts={}
    for source in ("deepcad","fusion360"):
        for level in ("simple","medium","hard"):
            pool=sorted((r for r in valid if r["dataset"]==source and difficulty(r["operation_count"])==level),key=lambda r:r["cad_id"])
            # First remove duplicates within this candidate pool using all identity keys.
            reps=[]; local={k:set() for k in keys}
            for r in pool:
                if any(r.get(k) in local[k] for k in keys if r.get(k)): continue
                reps.append(r)
                for k in keys:
                    if r.get(k): local[k].add(r[k])
            need=QUOTAS[source][level]; pool_counts[f"{source}_{level}"]=len(reps)
            if len(reps)<need: raise RuntimeError(f"insufficient {source}/{level}: {len(reps)} < {need}")
            # Midpoint-stratified proposals, followed by deterministic fill if a key was used in another stratum.
            idx=np.floor((np.arange(need)+0.5)*len(reps)/need).astype(int).tolist()
            order=[]
            for j in idx+list(range(len(reps))):
                if j not in order: order.append(j)
            accepted=[]
            for j in order:
                r=reps[j]
                if any(r.get(k) in used[k] for k in keys if r.get(k)): continue
                accepted.append(r)
                for k in keys:
                    if r.get(k): used[k].add(r[k])
                if len(accepted)==need: break
            if len(accepted)<need: raise RuntimeError(f"dedup fill failed {source}/{level}: {len(accepted)} < {need}")
            chosen.extend(accepted)
    chosen.sort(key=lambda r:r["cad_id"])
    if len(chosen)!=1000 or len({r["cad_id"] for r in chosen})!=1000: raise RuntimeError("cohort is not 1000 unique CADs")
    audit={"cohort_size":1000,"source_counts":dict(Counter(r["dataset"] for r in chosen)),"difficulty_counts":dict(Counter(f"{r['dataset']}:{difficulty(r['operation_count'])}" for r in chosen)),"pool_counts_after_cross_split_filter_and_dedup":pool_counts,"excluded_cross_split_identity":excluded_cross,"excluded_missing_required_input":excluded_missing,"cross_split_leakage":0}
    return chosen,audit


def run_arm(model, arm, surface_tokens, packed, input_ids, record):
    original_geometry=model.forward_geometry; original_splice=module._splice_geometry; state={}
    def precomputed(self,surface_points,edge_points=None,device=None,dtype=None): return surface_tokens,packed.tokens.unsqueeze(0).to(dtype=dtype)
    def masked_splice(cur_embeds,cur_mask,regions):
        masks=[torch.ones(regions[0][1].shape[0],dtype=torch.bool,device=cur_mask.device),packed.attention_mask]
        out_emb,out_mask=splice_geometry_masked(cur_embeds,cur_mask,regions,masks)
        pad=~packed.attention_mask
        off=(regions[0][0]+1)+regions[0][1].shape[0]+(regions[1][0]-regions[0][2]+1)
        real=out_mask[off:off+packed.padded_length].bool()
        state.update(physical_padded_length=int(regions[1][1].shape[0]),second_stream_active=int(packed.attention_mask.sum()),fake_valid_padding=int(real[packed.valid_count:].sum()),padding_attention=int(real[pad].sum()))
        return out_emb,out_mask
    def hook(mod,args,kwargs):
        state["total_llm_input_length"]=int(kwargs["inputs_embeds"].shape[1]); state["total_active_attention"]=int(kwargs["attention_mask"].sum()); raise StopAtLlamaEntry()
    model.forward_geometry=types.MethodType(precomputed,model); module._splice_geometry=masked_splice
    handle=model.model.register_forward_pre_hook(hook,with_kwargs=True)
    try:
        try:
            dummy=torch.zeros((1,1,9),device=input_ids.device)
            with torch.no_grad(): model(input_ids=input_ids,attention_mask=torch.ones_like(input_ids),point_clouds=dummy,edge_clouds=dummy)
        except StopAtLlamaEntry: pass
    finally:
        handle.remove(); model.forward_geometry=original_geometry; module._splice_geometry=original_splice
    record[arm]=state


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); ap.add_argument("--device",default="cuda:0"); ap.add_argument("--asset-root"); ap.add_argument("--canonical-asset-root",help="Frozen first-pass assets used by verification reruns"); ap.add_argument("--select-only",action="store_true"); ap.add_argument("--debug-ids",help="JSON list; diagnostic subset only")
    args=ap.parse_args(); out=pathlib.Path(args.output); out.mkdir(parents=True,exist_ok=False)
    cohort,cohort_audit=select_cohort()
    cohort_doc={"selection_protocol":"train-only, geometry-valid, cross-split identity filtered, source+difficulty midpoint-stratified","quotas":QUOTAS,"audit":cohort_audit,"cad_ids":[r["cad_id"] for r in cohort]}
    cohort_doc["content_sha256"]=canonical_hash(cohort_doc)
    (out/"COHORT.json").write_text(json.dumps(cohort_doc,indent=2)+"\n")
    if args.select_only:
        print(json.dumps(cohort_audit,indent=2)); return
    if args.debug_ids:
        wanted=set(json.loads(pathlib.Path(args.debug_ids).read_text()))
        cohort=[r for r in cohort if r["cad_id"] in wanted]
        if len(cohort)!=len(wanted): raise RuntimeError("debug ID not in frozen cohort")
    asset_root=pathlib.Path(args.asset_root) if args.asset_root else None
    if asset_root: asset_root.mkdir(parents=True,exist_ok=False)
    if file_sha(C2_CKPT)!=C2_CKPT_SHA256: raise RuntimeError("C2 checkpoint hash drift")
    torch.manual_seed(42); np.random.seed(42); torch.use_deterministic_algorithms(True,warn_only=False)
    heldout_geometry.install()
    plugin=get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True)
    model=module.SpatialLMLlamaForCausalLM.from_pretrained(ROOT/'SpatialLM/models/SpatialLM1.1-Llama-1B',torch_dtype=torch.bfloat16,device_map=args.device,local_files_only=True).eval()
    b1_proj=copy.deepcopy(model.point_proj); m2_proj=build_curve_projector(256,model.config.hidden_size).to(device=args.device,dtype=torch.bfloat16).eval(); model.edge_proj=b1_proj
    ids=torch.tensor([[128000,model.point_start_token_id,model.point_token_id,model.point_end_token_id,model.edge_start_token_id,model.edge_token_id,model.edge_end_token_id,1]],device=args.device)
    rows=[]; reencode=[]
    for n,rec in enumerate(cohort,1):
        pack=pathlib.Path(rec["pack"]); surface_path=pack/"surface_points.npy"; target_path=pack/"cad_target.dsl"; edge_path=pack/"edge_points_gt_sharp.npy"
        surface,edge=plugin._load_cad_separate_edge(str(surface_path)); curve=load_curve_tokens(surface_path)
        curve_path=pathlib.Path(load_curve_tokens.__globals__["resolve_curve_token_path"](surface_path))
        meta_path=curve_path.with_name("curve_tokens_meta.json"); curve_meta=json.loads(meta_path.read_text())
        curve_data_dir=ROOT/"ours3/curve_token_data_v1"/("deepcad_train" if rec["dataset"]=="deepcad" else "fusion360_train")/rec["sample_id"]
        raw_curve_path=curve_data_dir/"curve_samples.npz"
        with torch.no_grad():
            surface_tokens=model.forward_point_cloud(torch.tensor(surface,device=args.device),args.device,torch.bfloat16,projector=model.point_proj)
            b1_raw=model.forward_point_cloud(torch.tensor(edge,device=args.device),args.device,torch.bfloat16,projector=b1_proj).squeeze(0)
            m2_raw=m2_proj(torch.tensor(curve,device=args.device,dtype=torch.bfloat16))
        k=shared_k_valid(len(b1_raw),len(m2_raw),K_CAP); b1=pack_stream(b1_raw,k,K_CAP); m2=pack_stream(m2_raw,k,K_CAP)
        b1_np=b1_raw.float().cpu().numpy().astype(np.float16); b1_sha=hashlib.sha256(b1_np.tobytes()).hexdigest()
        b1_mask=b1.attention_mask.cpu().numpy(); m2_mask=m2.attention_mask.cpu().numpy()
        rel=f"records/{rec['cad_id']}"
        if asset_root:
            rd=asset_root/rel; rd.mkdir(parents=True,exist_ok=False)
            np.save(rd/"b1_full_tokens_fp16.npy",b1_np); np.save(rd/"b1_mask.npy",b1_mask); np.save(rd/"m2_mask.npy",m2_mask)
        elif args.canonical_asset_root:
            frozen=np.load(pathlib.Path(args.canonical_asset_root)/rel/"b1_full_tokens_fp16.npy")
            if frozen.shape!=b1_np.shape: raise RuntimeError(f"B1 frozen shape drift {rec['cad_id']}")
            absdiff=np.abs(frozen.astype(np.float32)-b1_np.astype(np.float32))
            max_diff=float(absdiff.max()) if absdiff.size else 0.0
            if not np.isfinite(max_diff):
                raise RuntimeError(f"B1 recompute non-finite {rec['cad_id']}: {max_diff}")
            # Frozen bytes remain the training identity. Cross-GPU / spconv fp16
            # fluctuation is recorded, not treated as a new canonical version.
            b1_sha=hashlib.sha256(frozen.tobytes()).hexdigest()
            reencode.append({"cad_id":rec["cad_id"],"bitwise_identical":bool(frozen.tobytes()==b1_np.tobytes()),"max_abs_diff":max_diff,"n_changed":int((frozen.view(np.uint16)!=b1_np.view(np.uint16)).sum())})
        ops=rec.get("operation_names",[]); target=target_path.read_text()
        row={
            "cad_id":rec["cad_id"],"source_dataset":rec["dataset"],"split":"train","difficulty_bin":difficulty(rec["operation_count"]),"operation_count":rec["operation_count"],"operation_names":ops,
            "surface_input":str(surface_path),"target_dsl":str(target_path),"target_dsl_sha256":file_sha(target_path),"target_dsl_chars":len(target),
            "b1_full_input":str(edge_path),"b1_full_tokens":f"{rel}/b1_full_tokens_fp16.npy","b1_full_tokens_sha256":b1_sha,"b1_post_encoder_count":len(b1_raw),
            "m2_full_curves":str(raw_curve_path),"m2_full_c2_tokens":str(curve_path),"m2_full_c2_tokens_sha256":file_sha(curve_path),"m2_available_count":len(m2_raw),
            "k_cap":K_CAP,"k_valid":k,"selected_b1_indices":list(b1.selected_indices),"selected_m2_indices":list(m2.selected_indices),
            "b1_mask":f"{rel}/b1_mask.npy","m2_mask":f"{rel}/m2_mask.npy","physical_padded_length":K_CAP,
            "b1_retention_ratio":k/len(b1_raw),"m2_retention_ratio":k/len(m2_raw),
            "curve_type_counts":curve_meta["type_counts"],"has_circle":("Circle" in ops),"has_rectangle":("Box" in ops),"has_polygon":("ExtrudePolygon" in ops),"has_cut":("Cut" in ops),"has_join":("Union" in ops),"has_hole":("Circle" in ops and "Cut" in ops),
            "provenance":{"curve_encoder_checkpoint":"ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt","curve_encoder_checkpoint_sha256":C2_CKPT_SHA256,"curve_encoder_frozen":True,"curve_token_root":"ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2","budget_protocol":"min(B1_post_encoder_count,M2_available_count,K_cap)","selection_protocol":"deterministic integer midpoint stratification"},
        }
        run_arm(model,"B1",surface_tokens,b1,ids,row); run_arm(model,"M2",surface_tokens,m2,ids,row)
        row.update(budget_equality=row["B1"]["second_stream_active"]==row["M2"]["second_stream_active"]==k,attention_equality=row["B1"]["second_stream_active"]==row["M2"]["second_stream_active"],total_attention_equality=row["B1"]["total_active_attention"]==row["M2"]["total_active_attention"],physical_length_equality=row["B1"]["physical_padded_length"]==row["M2"]["physical_padded_length"]==K_CAP,fake_valid_padding=row["B1"]["fake_valid_padding"]+row["M2"]["fake_valid_padding"],padding_attention=row["B1"]["padding_attention"]+row["M2"]["padding_attention"])
        row["record_sha256"]=canonical_hash(row); rows.append(row)
        extra=""
        if reencode and reencode[-1]["cad_id"]==rec["cad_id"]:
            extra=f" dB1={reencode[-1]['max_abs_diff']:.8f} bitwise={int(reencode[-1]['bitwise_identical'])}"
        print(f"{n:04d}/{len(cohort)} {rec['cad_id']} B1={len(b1_raw)} M2={len(m2_raw)} K={k}{extra}",flush=True)
        if not(row["budget_equality"] and row["attention_equality"] and row["total_attention_equality"] and row["physical_length_equality"] and row["fake_valid_padding"]==0 and row["padding_attention"]==0):
            (out/"HARD_STOP.json").write_text(json.dumps(row,indent=2)); raise RuntimeError(f"hard gate failed {rec['cad_id']}")
    if reencode:
        (out/"B1_REENCODE.json").write_text(json.dumps({"n":len(reencode),"bitwise_identical":sum(x["bitwise_identical"] for x in reencode),"max_abs_diff":max(x["max_abs_diff"] for x in reencode),"rows":reencode},indent=2)+"\n")
    manifest={"protocol":"B1_POST_ENCODER_BUDGET_C2_V2_1K","k_cap":K_CAP,"cohort":cohort_doc,"cohort_size":1000,"views":{"B0":"surface+target","B1-BM":"canonical B1 selection+mask","M2-C2-BM":"canonical M2 selection+mask"},"rows":rows}
    if args.debug_ids: manifest["diagnostic_subset"]=True
    manifest["content_sha256"]=canonical_hash(manifest); (out/"MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("MANIFEST_SHA256="+manifest["content_sha256"])

if __name__=="__main__": main()
