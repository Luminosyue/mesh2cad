"""Fail-closed dimensional transform for the observed Fusion360 DSL grammar."""
import ast, math
LENGTHS={'Circle':{'radius'},'Box':{'width','depth','height','height_two'},'Extrude':{'height','height_two'},'ExtrudePolygon':{'height','height_two'}}
PRESERVE={'Box':{'axis','x_axis','symmetric'},'Extrude':{'axis','symmetric'},'ExtrudePolygon':{'axis','x_axis','symmetric'},'Circle':set()}
def transform(code,scale,translation=(0.,0.,0.)):
 if not math.isfinite(scale) or scale<=0:raise ValueError('positive finite scale required')
 if len(translation)!=3 or not all(math.isfinite(x) for x in translation):raise ValueError('invalid translation')
 tree=ast.parse(code)
 def number(n):
  v=ast.literal_eval(n)
  if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):raise ValueError('nonliteral length')
  return v
 def scalar(n):return ast.Constant(number(n)*scale)
 def vector(n,offset):
  if not isinstance(n,(ast.Tuple,ast.List)) or len(n.elts)!=len(offset):raise ValueError('invalid vector dimension')
  return type(n)(elts=[ast.Constant(number(x)*scale+t) for x,t in zip(n.elts,offset)],ctx=ast.Load())
 class Convert(ast.NodeTransformer):
  def visit_Call(self,n):
   if not isinstance(n.func,ast.Name):raise ValueError('indirect call')
   op=n.func.id
   if op in ('Cut','Union'):
    if len(n.args)!=2 or n.keywords:raise ValueError('boolean grammar')
    return self.generic_visit(n)
   if op not in LENGTHS:raise ValueError('unsupported dimensional schema: '+op)
   if op=='Extrude':
    if len(n.args)!=1 or not isinstance(n.args[0],(ast.Call,ast.Name)):raise ValueError('unsupported Extrude shorthand')
    n.args=[self.visit(n.args[0])]
   elif n.args:raise ValueError('unsupported positional grammar: '+op)
   seen=set()
   for k in n.keywords:
    if k.arg in seen:raise ValueError('duplicate keyword')
    seen.add(k.arg)
    if k.arg in LENGTHS[op]:k.value=scalar(k.value)
    elif k.arg=='origin' and op!='Circle':k.value=vector(k.value,translation)
    elif k.arg=='points' and op=='ExtrudePolygon':
     if not isinstance(k.value,(ast.Tuple,ast.List)):raise ValueError('nonliteral polygon')
     k.value.elts=[vector(v,(0,0)) for v in k.value.elts]
    elif k.arg not in PRESERVE[op]:raise ValueError('unknown dimensional keyword: '+str(k.arg))
   # Missing defaults could be dimensional; do not silently transform them.
   required={'Circle':{'radius'},'Box':{'width','depth','height','origin'},'Extrude':{'height','origin'},'ExtrudePolygon':{'points','height','origin'}}[op]
   if not required<=seen:raise ValueError('implicit dimensional defaults')
   return n
 for stmt in tree.body:
  if not isinstance(stmt,ast.Assign) or not isinstance(stmt.value,(ast.Call,ast.Name)):raise ValueError('unsupported assignment grammar')
 return ast.unparse(ast.fix_missing_locations(Convert().visit(tree)))+'\n'
