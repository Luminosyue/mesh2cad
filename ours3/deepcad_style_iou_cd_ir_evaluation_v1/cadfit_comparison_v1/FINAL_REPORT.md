# P1 vs CADFit DeepCAD-style IoU/CD/IR VAL1000

FULL_N=1000
FROZEN_GT_VALID_N=253
COMMON_VALID_N=203

| Method | IR | Invalid N | IoU mean | IoU median | CD mean | CD median |
|---|---:|---:|---:|---:|---:|---:|
| P1 | 0.062000 | 62 | 0.544403 | 0.643568 | 39318.085218 | 0.002342 |
| CADFit | 0.045000 | 45 | 0.877443 | 0.989997 | 31.922378 | 0.000977 |

IOU_DELTA_P1_MINUS_CADFIT=-0.33303998820961106
IOU_95CI=[-0.3906200923875621, -0.2740002256744082]
CD_DELTA_P1_MINUS_CADFIT=39286.162839910256
CD_95CI=[7588.636938858235, 82258.53848803339]
IR_MCNEMAR_P=0.08568897435916664

CADFit STL outputs were inverse-normalized using input-only center and scale. IoU uses OCC solids and Booleans. CD uses 2000 deterministic surface samples, squared bidirectional directional means summed. Out-of-range Boolean IoU values are classified as IoU failures and excluded from strict common-valid comparison, not clamped.
