# Fresh Test Freeze Policy

No fresh train/val/test split was created because the verified cohort is below the minimum 200 records. Test data from Heldout25 remains excluded and unread for this pilot.

When a future cohort reaches the minimum, use a complexity-stratified 70/15/15 split, freeze the manifest before training, and read TEST only once after the method is frozen.
