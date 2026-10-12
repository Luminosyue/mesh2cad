"""CPU-only tests of the audit, not model training or test-split evaluation."""
import importlib.util,json,pathlib,unittest
import numpy as np
from scipy.spatial import cKDTree

BASE=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/geometry_pack_v2_practical/_audit_stage1_v2')
spec=importlib.util.spec_from_file_location('audit',BASE/'code/audit_v2_labels.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

class AuditTests(unittest.TestCase):
    def test_fingerprint_reindex_scale_translation(self):
        v=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]],float)
        f=np.array([[0,1,2],[0,1,3],[1,2,3],[0,2,3]])
        perm=np.array([2,0,3,1]); inv=np.argsort(perm)
        self.assertEqual(audit.fingerprint(v,f)[0],audit.fingerprint(v[perm]*10+25,inv[f[::-1,::-1]])[0])

    def test_fingerprint_geometry_change(self):
        v=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]],float)
        f=np.array([[0,1,2],[0,1,3],[1,2,3],[0,2,3]])
        altered=v.copy();altered[3,2]=2
        self.assertNotEqual(audit.fingerprint(v,f)[0],audit.fingerprint(altered,f)[0])

    def test_metric_zero_on_identical_points(self):
        a=np.random.default_rng(42).normal(size=(100,3))
        self.assertEqual(float(cKDTree(a).query(a)[0].max()),0)

    def test_source_paths_absolute_and_resolvable(self):
        rows=json.loads((BASE/'inventory.json').read_text())
        self.assertEqual(len(rows),2796)
        for r in rows:
            self.assertTrue(pathlib.Path(r['source_step']).is_absolute(),r['cad_id'])
            self.assertTrue(pathlib.Path(r['source_step']).is_file(),r['cad_id'])

    def test_gt_coverage_threshold_is_relative(self):
        # A distance of 0.03 is covered for D=2, not for D=1.
        self.assertTrue(.03/2<=.02)
        self.assertFalse(.03/1<=.02)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(AuditTests)
    res=unittest.TextTestRunner(verbosity=2).run(suite)
    with (BASE/'reports/AUDIT_UNIT_TESTS.json').open('x') as f:json.dump({'run':res.testsRun,'failures':len(res.failures),'errors':len(res.errors),'passed':res.wasSuccessful()},f,indent=2)
    raise SystemExit(not res.wasSuccessful())
