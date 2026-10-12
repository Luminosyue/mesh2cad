# Controlled Tank Stress Test

This case extends the original six-case suite with a 22-part synthetic tank.

## Parts
- 6 boxes: lower hull, upper hull, two turret boxes, left/right tracks
- 2 elongated cylinders: main gun and antenna
- 14 short/wide cylinders: muzzle brake, hatch, and 12 road wheels

## Results
- Input: 35,756 vertices, 71,424 faces, 22 parts
- Low-poly: 18,632 vertices, 37,176 faces
- Face reduction: 47.95%
- Primitive type accuracy: 8/22 = 36.36%
- Normalized Chamfer: 0.003677
- Normalized Hausdorff: 0.018947

## Interpretation
The current PCA rule correctly recovers the 6 boxes, the long gun barrel, and the antenna. It misclassifies all short/wide cylinders (road wheels, hatch, muzzle brake) as boxes. This is an intentional stress test showing that the current recognizer is not yet suitable for a realistic tank.

## Run
```bash
python -c "from run_batch_cases import run_case, case_controlled_tank; run_case('controlled_tank', case_controlled_tank())"
```

STEP export (in CadQuery/OCP environment):
```bash
python export_steps_batch.py
```
