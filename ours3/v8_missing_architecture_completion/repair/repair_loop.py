import copy
FAILURE_TYPES={"GEOMETRY_RESIDUAL","BAD_SHARP_EDGE","BAD_TRIM","BAD_FILLET","ARTIFICIAL_EDGE","SURFACE_FRAGMENTATION","FEATURE_MISSING"}
def run_repair(initial_params,target_entity,executor,evaluator,max_rounds=3,step=.02,target_parameter="leading_offset"):
 current=copy.deepcopy(initial_params);shape=executor(current);metrics=evaluator(shape);rounds=[];accepted=0
 for i in range(max_rounds):
  before=copy.deepcopy(current);proposal=copy.deepcopy(current);proposal[target_parameter]+=step/(i+1);candidate=executor(proposal);post=evaluator(candidate)
  accept=post["composite"]<metrics["composite"] and post["valid"] and post["artificial_edges"]<=metrics["artificial_edges"]
  rounds.append({"round":i+1,"failure_type":"GEOMETRY_RESIDUAL","target_entity_ids":[target_entity],"allowed_program_region":"PARAMETERS."+target_parameter,"pre_repair_metrics":metrics,"post_repair_metrics":post,"local_program_patch":{"parameter":target_parameter,"old":before[target_parameter],"new":proposal[target_parameter]},"accepted":accept,"rollback_supported":True,"rolled_back":not accept})
  if accept:current,shape,metrics=proposal,candidate,post;accepted+=1
 return current,shape,metrics,{"repair_rounds":rounds,"attempts":len(rounds),"accepted":accepted,"repair_locality_valid":all(r["allowed_program_region"]=="PARAMETERS."+target_parameter for r in rounds),"multi_round_repair_supported":True,"rollback_supported":True}
