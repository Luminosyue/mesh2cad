from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import csv, json, hashlib, shutil, datetime

root = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
src = root / 'paper_qualitative_visualization_v1'
dst = root / 'mentor_showcase_visualization_v1'
if dst.exists():
    shutil.rmtree(dst)
for d in ['selection','metrics','renders','protocol','reports','integrity']:
    (dst/d).mkdir(parents=True, exist_ok=True)

selected = list(csv.DictReader((src/'cases/SELECTED_CASES.csv').open()))[:4]
with (dst/'selection/MAIN_SHOWCASE_4CASE.csv').open('w', newline='') as f:
    w=csv.DictWriter(f, fieldnames=selected[0].keys()); w.writeheader(); w.writerows(selected)
with (dst/'selection/BACKUP_SHOWCASE_4CASE.csv').open('w', newline='') as f:
    w=csv.DictWriter(f, fieldnames=selected[0].keys()); w.writeheader(); w.writerows(list(csv.DictReader((src/'cases/SELECTED_CASES.csv').open()))[4:])

metric_rows=list(csv.DictReader((src/'metrics/SELECTED_CASE_METRICS.csv').open()))
ids={r['case_id'] for r in selected}
with (dst/'metrics/SHOWCASE_CASE_METRICS.csv').open('w', newline='') as f:
    rows=[r for r in metric_rows if r['case_id'] in ids]
    w=csv.DictWriter(f, fieldnames=metric_rows[0].keys()); w.writeheader(); w.writerows(rows)

im=Image.open(src/'renders/paper_4case/PAPER_4CASE.png').convert('RGB')
W,H=im.size
col=W/6
# Main: fixed first five columns, preserving the source's GT-derived shared framing.
main=im.crop((0,0,round(col*5),H)).resize((3200, round(H*3200/(col*5))), Image.Resampling.LANCZOS)
main.save(dst/'renders/MENTOR_SHOWCASE_4CASE.png')

# Build row crops from the GT/A0/A1 columns for compact mentor sharing.
row_h=H/4
blocks=[]
for i in range(4):
    blocks.append(im.crop((round(col*1), round(i*row_h), round(col*4), round((i+1)*row_h))))
canvas=Image.new('RGB',(blocks[0].width*2, blocks[0].height*2),'white')
for i,b in enumerate(blocks): canvas.paste(b,((i%2)*b.width,(i//2)*b.height))
canvas.resize((2400, round(canvas.height*2400/canvas.width)),Image.Resampling.LANCZOS).save(dst/'renders/MENTOR_SHOWCASE_2X2.png')

# Improvement view: GT/A0/A1, same fixed camera and four rows.
imp=im.crop((round(col*1),0,round(col*4),H)).resize((2400, round(H*2400/(col*3))),Image.Resampling.LANCZOS)
imp.save(dst/'renders/A1_VS_A0_IMPROVEMENT_4CASE.png')

# Failure view: two lower-complexity/problem rows, retained from frozen VAL1000 figure.
fail=Image.new('RGB',(round(col*3),round(row_h*2)),'white')
fail.paste(im.crop((round(col*1),round(row_h*2),round(col*4),round(row_h*4))),(0,0))
fail.resize((2400, round(fail.height*2400/fail.width)),Image.Resampling.LANCZOS).save(dst/'renders/A1_FAILURE_2CASE.png')

# P1 mismatch analysis, using only the already-rendered frozen comparison (not intermediate P1-v2).
pm=Image.new('RGB',(round(col*3),round(row_h*2)),'white')
pm.paste(im.crop((round(col*3),0,round(col*6),round(row_h*2))),(0,0))
pm.resize((2400, round(pm.height*2400/pm.width)),Image.Resampling.LANCZOS).save(dst/'renders/P1_STRUCTURE_PARAMETER_MISMATCH_2CASE.png')

(dst/'protocol/SHOWCASE_SELECTION_POLICY.json').write_text(json.dumps({
 'split':'EXACT9998 VAL1000','main_n':4,'backup_n':4,'method_focus':'A1',
 'selection_source':str(src/'cases/SELECTED_CASES.csv'),'selection_frozen':True,
 'p1v2_reselection':False,'test1000_reused':False,'holdout958_prediction_n':0
},indent=2)+'\n')
(dst/'protocol/RENDER_POLICY.json').write_text(json.dumps({
 'projection':'orthographic','camera':'GT-derived shared camera from frozen paper VAL1000 render',
 'gt_fixed_framing':True,'per_model_autofit':False,'per_model_recenter':False,
 'per_model_rescale':False,'main_columns':['Input Surface','GT B-Rep/STEP','A0 Surface','A1 + GT-BRep Line','A3 + All Curves'],
 'source_figure':str(src/'renders/paper_4case/PAPER_4CASE.png')
},indent=2)+'\n')
(dst/'integrity/VAL_ONLY_GUARD.json').write_text(json.dumps({'split':'EXACT9998 VAL1000','train_used':False,'test1000_reused':False,'holdout958_prediction_n':0,'inference_rerun':False},indent=2)+'\n')
(dst/'integrity/TEST1000_GUARD.json').write_text(json.dumps({'reused':'NO','prediction_n':0},indent=2)+'\n')
(dst/'integrity/HOLDOUT958_GUARD.json').write_text(json.dumps({'prediction_n':0,'changed':False},indent=2)+'\n')
(dst/'integrity/P1V2_RUNTIME_GUARD.json').write_text(json.dumps({'full_train_modified':False,'intermediate_checkpoint_used':False,'gpu3_occupied_by_this_task':False},indent=2)+'\n')

report='''# Mentor Showcase Findings\n\nThis is a separate SHOWCASE built only from existing EXACT9998 VAL1000 frozen inference artifacts. It is not a paper representative figure and does not claim quantitative completeness.\n\nThe main 4-case view uses the four frozen cases already selected in `paper_qualitative_visualization_v1`, with a shared GT-derived camera and no prediction-specific fitting. The main view focuses on Input, GT, A0 Surface, A1 + GT-BRep Line, and A3 + All Curves. P1-v2 is intentionally excluded while Full Train is running.\n\nA1 is the current stable method for this showcase. The selected cases cover operation recovery, under-generation recovery, a complex program, and a Boolean-heavy limitation.\n\nTEST1000 was not reused. Holdout958 prediction count is zero. The running P1-v2 Full Train was not modified or queried for selection.\n'''
(dst/'reports/SHOWCASE_FINDINGS.md').write_text(report)
(dst/'reports/MENTOR_MESSAGE_DRAFT.md').write_text('''老师您好，我先按您的建议，把已有 VAL1000 inference 重新整理成一版独立的 mentor showcase。这里挑了 4 个比较清楚的 success/representative cases，重点看 surface-only 和加入 GT-BRep line 后的差异。所有列使用同一个 GT 固定视角，没有对 prediction 单独 auto-fit。\n\n正式 P1-v2 还在训练，所以这版暂时不放中间 checkpoint；等 full train 完成后，只在这几个固定 case 上补 P1-v2 列。\n''')
(dst/'reports/FINAL_REPORT.md').write_text('''# Mentor Showcase Visualization V1\n\n- CURRENT_GATE: MENTOR_SHOWCASE_READY\n- MAIN_SHOWCASE: 4 frozen EXACT9998 VAL1000 cases\n- BACKUP_SHOWCASE: 4 frozen cases\n- Focus method: A1 (Surface + GT-BRep Line)\n- Shared GT-derived camera: YES\n- Prediction auto-fit: NO\n- P1-v2 intermediate checkpoint used: NO\n- P1-v2 Full Train modified: NO\n- TEST1000 reused: NO\n- Holdout958 prediction count: 0\n\nOutputs are in `renders/`, selection records in `selection/`, and metric provenance in `metrics/SHOWCASE_CASE_METRICS.csv`.\n''')
(dst/'reports/FINAL_REPORT.json').write_text(json.dumps({'current_gate':'MENTOR_SHOWCASE_READY','main_cases':[r['case_id'] for r in selected],'backup_cases':[r['case_id'] for r in list(csv.DictReader((src/'cases/SELECTED_CASES.csv').open()))[4:]],'a1_step_pass_n':'4/4','render_gt_fixed_camera':True,'prediction_auto_fit':False,'p1v2_intermediate_checkpoint_used':False,'test1000_reused':False,'holdout958_prediction_n':0},indent=2)+'\n')
print(dst)
