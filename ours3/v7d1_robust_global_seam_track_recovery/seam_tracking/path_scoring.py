"""Scale-relative global seam scoring components."""
import numpy as np
def turning_angle(a,b,c):
    x=np.asarray(b)-np.asarray(a);y=np.asarray(c)-np.asarray(b)
    return float(np.arccos(np.clip(np.dot(x,y)/(np.linalg.norm(x)*np.linalg.norm(y)+1e-15),-1,1)))
def pair_residual_score(distance,diagonal): return float(np.exp(-distance/max(diagonal*.08,1e-15)))
