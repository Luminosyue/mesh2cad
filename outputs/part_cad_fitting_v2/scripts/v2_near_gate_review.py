from v2_common import *
from collections import Counter

assert read(O/'integrity/NUMERIC_REPAIR_near.json')['parameters_and_candidate_ids_unchanged']
rows=[r for r in read(O/'manifests/cases.json') if r['v1_status']=='NEAR_PASS']
results=[read(O/'cases'/r['case_id']/'result.json') for r in rows]
assert len(results)==63
assert not any(c.get('execution',{}).get('error')=='Disallowed CAD operation: float64' for r in results for c in r['attempts'])
counts=Counter(r['v2_status'] for r in results)
checks=Counter(k for r in results if r['v2_status']!='STRICT_ACCEPT' for k in failed(r['v2_metrics']))
methods=Counter(r['fix_type'] for r in results if r['v2_status']=='STRICT_ACCEPT')
baseline=sum(r['selected_candidate']==0 for r in results)
analysis=[
 f"Corrected Near cohort: {counts['STRICT_ACCEPT']} Strict, {counts['NEAR_PASS']} Near, {counts['REJECT']} Reject; rescue rate {counts['STRICT_ACCEPT']/63:.2%}.",
 'The initial scalar-serialization parser defect prevented numeric candidates from running. It has been fixed and affected candidates rebuilt with identical parameter values. Initial reports are superseded, not treated as geometric evidence.',
 f'Remaining failed strict checks (overlapping): {dict(checks)}. Baseline selected in {baseline} cases. Successful methods: {dict(methods)}.',
 'Three bounded coordinate sweeps and fixed structure limit the reachable shapes. The warped IoU64/4000-point optimization proxy can disagree with reloaded IoU128/20000-point evaluation, especially for thin geometry. This is a limitation, not proof of a global optimum.',
 'Closed-section extraction can fail or miss topology. An inspected numerical Strict rescue closes a visible source opening. Open segmentation surfaces versus closed CAD can also cause a centroid mismatch; these issues need topology-aware fitting rather than looser thresholds.',
 f"The weighted ranking produces {counts['REJECT']} Near-to-Reject changes despite score improvement; these are explicitly reported as classification regressions.",
 'Continue the authorized 142 Reject cases with bounded structure alternatives only after this corrected Near analysis. No new objects, threshold changes, training or assembly.'
]
gate={'near_completed_n':63,'near_to_strict_n':counts['STRICT_ACCEPT'],'near_still_near_n':counts['NEAR_PASS'],'near_to_reject_n':counts['REJECT'],'rescue_rate':counts['STRICT_ACCEPT']/63,'remaining_failed_checks':dict(checks),'baseline_selected_n':baseline,'analysis':analysis,'numeric_serialization_bug_corrected':True,'reject_stage_allowed':True}
dump(O/'reports/NEAR_GATE.json',gate)
(O/'reports/NEAR_LOW_RESCUE_ANALYSIS.md').write_text('# Corrected Near-stage rescue analysis\n\n'+'\n\n'.join(analysis)+'\n')
print(json.dumps(gate,indent=2))
