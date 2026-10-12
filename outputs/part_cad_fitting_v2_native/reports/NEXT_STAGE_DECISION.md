# Next stage decision

REPRESENTATION_GATE = PASS
PART_GEOMETRY_GATE = FAIL
CAN_START_REASSEMBLY_V2 = NO
CAN_SCALE_TO_100_OBJECTS = NO
NEXT_ALLOWED_STAGE = TARGETED_PROFILE_AND_STRUCTURE_DIAGNOSIS

Operational geometry readiness requires at least 20 Strict and major-part Strict >=30%; neither this decision nor the target relaxes per-part strict criteria. Scale100 is prohibited this round even if part targets pass; object reassembly quality has not been improved or evaluated here. Remaining blocker: Major-part geometry fidelity and unsupported/missing geometric detail.

Near-stage pause gate: {'near_input_n': 63, 'near_to_strict_n': 11, 'near_still_near_n': 52, 'near_to_reject_n': 0, 'rescue_rate': 0.1746031746031746, 'new_strict_vs_baseline_n': 2, 'inherited_baseline_strict_n': 9, 'reject_stage_allowed': True, 'decision': 'PROCEED_REJECT'}. If blocked, 142 Reject were not refit; their retained results remain in the 209 paired table with fitting_performed=false. Review profile/family/parameter evidence before a further recovery round.
