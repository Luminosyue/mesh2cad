#!/usr/bin/env python3
import json, re, statistics
from collections import Counter
from pathlib import Path

ROOT = Path("ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/phase_d_inference_diagnostic_v1")
OPS = re.compile(r"\b(Box|Cylinder|ExtrudePolygon|Extrude|Revolve|Union|Cut|Intersect|Circle|Rectangle|Polygon)\s*\(")

def f1(a, b):
    a, b = Counter(a), Counter(b)
    tp = sum((a & b).values())
    if not a and not b: return 1.0
    if not tp: return 0.0
    p, r = tp/max(sum(b.values()),1), tp/max(sum(a.values()),1)
    return 2*p*r/(p+r)

def rep_ratio(xs, n):
    grams=[tuple(xs[i:i+n]) for i in range(max(0,len(xs)-n+1))]
    return 0.0 if not grams else 1-len(set(grams))/len(grams)

def loop_class(r):
    if not r.get("hit_max_new_tokens"): return "terminated"
    ids=r.get("last_100_token_ids",[])
    txt=r.get("last_100_tokens","")
    if rep_ratio(ids,4)>=0.65: return "token_ngram_loop"
    ops=OPS.findall(txt)
    if ops and max(Counter(ops).values())>=3: return "operation_loop"
    if r.get("dsl_parse_success") and "result" in r.get("prediction",""): return "valid_prefix_then_continues"
    if not r.get("dsl_parse_success"): return "syntax_drift"
    return "other_runaway"

def main():
    cohort=json.loads((ROOT/"data/phase_d_50.json").read_text())
    gt={r["cad_id"]:Path(r["target_dsl"]).read_text(errors="ignore") for r in cohort["records"]}
    summaries=[]
    per=[]
    for predp in sorted((ROOT/"runs").glob("*/predictions.jsonl")):
        rows=[json.loads(x) for x in predp.read_text().splitlines() if x.strip()]
        if len(rows)!=50: continue
        for r in rows:
            r["op_f1"]=f1(OPS.findall(gt[r["cad_id"]]),OPS.findall(r.get("prediction","")))
            r["repeat_1gram_ratio"]=rep_ratio(r.get("last_100_token_ids",[]),1)
            r["repeat_2gram_ratio"]=rep_ratio(r.get("last_100_token_ids",[]),2)
            r["repeat_4gram_ratio"]=rep_ratio(r.get("last_100_token_ids",[]),4)
            r["runaway_class"]=loop_class(r)
            r["variant"]=predp.parent.name
            per.append(r)
        lc=Counter(r["runaway_class"] for r in rows)
        summaries.append({
          "variant":predp.parent.name,"n":len(rows),
          "runaway_n":sum(bool(r.get("hit_max_new_tokens")) for r in rows),
          "runaway_rate":sum(bool(r.get("hit_max_new_tokens")) for r in rows)/len(rows),
          "eos_rate":sum(bool(r.get("eos_emitted")) for r in rows)/len(rows),
          "mean_generated_target_ratio":statistics.fmean(r["generated_to_target_ratio"] for r in rows),
          "dsl_parse_rate":sum(bool(r.get("dsl_parse_success")) for r in rows)/len(rows),
          "exact_rate":sum(bool(r.get("exact_match")) for r in rows)/len(rows),
          "mean_op_f1":statistics.fmean(r["op_f1"] for r in rows),
          "runaway_classes":dict(lc),
        })
    (ROOT/"PHASE_D_CORE_PER_CAD.jsonl").write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in per))
    report={"status":"CORE_METRICS_PASS_GEOMETRY_PENDING","variants":len(summaries),"samples_per_variant":50,"official_test_read":False,"training_started":False,"summary":summaries}
    (ROOT/"PHASE_D_CORE_SUMMARY.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2))

if __name__ == "__main__": main()
