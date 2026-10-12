# CAD Part Recovery V1

Status: `CAD_PART_RECOVERY_V1_COMPLETE`. Track F1 is `BLOCKED` solely because `CADPART_006` was rejected before inference by provider HTTP 403 `AllocationQuota.FreeTierOnly`; no historical geometry-identical STEP exists and no futile retry was made. Track F2 is `PASS`.

- F1 input: 4 frozen READY parts; historical results reused: 2; new part attempts: 2
- STEP available / independently BRep valid: 3 / 3
- Q1 / Q2 / Q3: 0 / 1 / 3
- Accepted pseudo CAD parts: 1 of 4; recovery rate: 0.25
- F2 review packets: 14 edges and 20 parts; human decisions applied: false
- Partial assembly pilot ready: false (1 accepted part)
- New P3/PhysX runs: 0/0; no assembly STEP, STEP GT, ABC data, or ICP
- Tests: 37 passed, 0 failed
- Blockers: F1=[QUOTA], F2=[]
