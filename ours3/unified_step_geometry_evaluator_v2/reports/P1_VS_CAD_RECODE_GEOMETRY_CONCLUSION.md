# P1 vs CAD-Recode Geometry Conclusion

V1 is invalid for cross-method geometry comparison because it omitted the official coordinate reconciliation. V2 applies the predefined official CAD-Recode transform in memory before all geometry measurements; it is not fitted to predictions.

P1 has higher STEP reload coverage (958/1000 vs 840/1000). On the 190 common geometry-valid cases, mean Chamfer is 24.3404 for P1 and 27.9912 for CAD-Recode; mean H95 is 46.7489 and 52.6228. The paired bootstrap conclusions are recorded in the frozen V2 statistics.

P1_STRONGER_THAN_CAD_RECODE=YES
COVERAGE_FIDELITY_TRADEOFF=NO
