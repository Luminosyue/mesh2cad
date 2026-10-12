from p1_debug_runtime import *
model,tok=load();batches=torch.load(DEBUG/'collated_batches.pt',weights_only=False);ids=json.loads((DEBUG/'batch_ids.json').read_text());rows=[]
for part in range(9):
 name=f'PART_{part:03d}';bs=[b for b,i in zip(batches,ids) if name+'__' in i];t=teacher(model,tok,bs,DEBUG/'teacher_all9'/name)
 rows.append({'part':name,'TOKEN_N':t['token_n'],'CORRECT_N':sum(r['correct'] for r in t['all_gt_tokens']),'EOS_N':len(t['blocks']),'EOS_CORRECT_N':sum(r['correct'] for r in t['all_gt_tokens'] if r['is_eos']),'TOKEN_ACC':t['token_acc'],'EOS_ACC':t['eos_acc'],'SEQUENCE_NLL':t['sequence_nll'],'MEAN_NLL':t['mean_nll']})
summary={'TRAIN_CASE_N':9,'BLOCK_N':134,'TOKEN_N':sum(r['TOKEN_N'] for r in rows),'TOKEN_ACC':sum(r['CORRECT_N'] for r in rows)/sum(r['TOKEN_N'] for r in rows),'EOS_ACC':sum(r['EOS_CORRECT_N'] for r in rows)/sum(r['EOS_N'] for r in rows),'parts':rows,'scope':'teacher forcing on all 134 original blocks, checkpoint-2000; not free-generation accuracy'}
save(DEBUG/'teacher_all9_summary.json',summary);print(json.dumps(summary),flush=True)
