import numpy as np
from scipy.optimize import minimize
def optimize(initial,executor,objective,max_iterations=12):
 names=list(initial);history=[]
 def run(x):
  params=dict(zip(names,map(float,x)));executed=executor(params);shape=executed[0] if isinstance(executed,tuple) else executed;loss,metrics=objective(shape);history.append({"parameters":params,"loss":loss,"metrics":metrics});return loss
 result=minimize(run,[initial[n] for n in names],method="Nelder-Mead",options={"maxiter":max_iterations,"xatol":1e-4,"fatol":1e-5})
 return dict(zip(names,map(float,result.x))),history,result
