from p1_debug_runtime import *
import inspect,shutil
import spatiallm.tuner.data.collator as collator
import spatiallm.tuner.data.template as template
import spatiallm.model.spatiallm_llama as lm
from transformers import DataCollatorForSeq2Seq
items=[]
for obj in [collator._encode_messages_example,collator.MultiModalDataCollatorForSeq2Seq.__call__,collator.SFTDataCollatorWith4DAttentionMask.__call__,DataCollatorForSeq2Seq.__call__,lm._splice_labels,lm.SpatialLMLlamaForCausalLM.prepare_inputs_for_generation,template.Template.fix_special_tokens,template.register_template]:
 src,line=inspect.getsourcelines(obj);item={'function':obj.__qualname__,'path':inspect.getsourcefile(obj),'line':line,'code':''.join(src)};items.append(item)
save(DEBUG/'evidence/label_mask_and_generation_sources.json',items)
save(DEBUG/'label_mask_audit.json',{'EOS_MASK_BUG_FOUND':'NO','pad_equals_eos':True,'observations':['target_label=target_ids preserves actual EOS','HF DataCollatorForSeq2Seq appends -100 labels for padding positions; does not mask by input token equality','multimodal _splice_labels masks only inserted geometry and final padding','runtime audit observed 134/134 block EOS active, including all 9 program final blocks'],'source_evidence':'evidence/label_mask_and_generation_sources.json','sample':'evidence/actual_collator_case0.json'})
# Reconstruct and expose the real decoder postprocessing/stopping without modifying it.
decoder=(OLD/'launch/cq54_decode.py').read_text()
save(DEBUG/'termination_logic_audit.json',{'serializer_literal_end':'# CAD_COMPLETE','all_final_targets_have_literal_end':all((Path(p['folder'])/'target_chunked.py').read_text().rstrip().endswith(END_MARKER) for p in json.loads((OLD/'data/parts.json').read_text())),'block_token_eos':'<|eot_id|>','per_block_eos_should_stop_program':False,'reason':'every supervised block ends with the same EOS; only the final block contains the CAD_COMPLETE marker','strip_special_tokens':True,'strip_special_tokens_discards_eos_for_text_but_generate_already_stops_on_eos':True,'padding_creates_additional_blocks':False,'max_new_tokens_is_only_stop':False,'old_script':decoder})
print('SOURCE_EVIDENCE_SAVED')
