"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b41e3e63867499cada873215bf255ee/part_005.stl', 'relative_path': '1b41e3e63867499cada873215bf255ee/part_005.stl', 'source_sha256': '824185a545a12c03b7e8f2daca45b5bb07e6d36b5dd92ca38362ce9700d0b075', 'input_faces': 170, 'input_vertices': 124, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12681372463703156, -0.18235237896442413, -0.25003090500831604], [0.12681372463703156, -0.08164762705564499, -0.15302614867687225]]}
GEOMETRY_BASE85 = 'c$}q}eN0wW9LLWC5-Okwr1%0{K^|TN<xN2#xV|IrV1N?Bg92$HASjBC?WV1l&DF|Y{$UILXwyn_DQbjrlh<WxwVI`_-5Jmy*=$*@t$%vX?|zAU?oL~)yPbVMem(cx-}#;Uob$UB=XuTuV&=7!x$f@$R`F$wH(wUS+Ur{n?AcY{wxX$}!@>N?=hu{;EG#Q1-tJ)S>}XV7ecP_qsB|SNvmq@iPKj!0ZavUi+f>usT365gO|^|}^=`jycWq0(``^)tNhxtka!j1ksr<)lwmXFGrVM?6#}eE>!nHds_WFRuHx|G@dwb04YhQgcOxjg+!|JQ>_1q6f1V1-rh<xX-H?2N{ujzinR^K%_=NjGj;Px%6ufS)Wu|rm0zkGN=)?bBh?{EAZ|1qg89u0oCJ)V2xm*_dR`6}=Y+kCZ>kc-scmQNMFfqd!@(#<@qoG|Zy#6A`LV=d&X6ZxOXeEoRusMYW8i=em--|U-K-v!@w=i0E<SLY=Tl3#w}mM}hiBcOdq7^i2#e9p7%bE~hwXAKUqe@*fg+4x4a>9as_e8s=$Bl7*k`1QG_ui4}8yg>QX?D>Juo)hz<MqKZu=OfSTtq5~IZ#ze=`JeLjGv4HDe~gV;eP+B*`PZCXqgG!X2qvGMePP7vE8`{R`*iO0VPX8qYV-a7`o@qjPE)R#{|jpbU+D^=_h0$pyFtN6{$0Nf2)>q6IUwzS%3<ceR~+AU{&pY5X^*G>m&+8dEq>Lbj^2OOHedCV4D<cB<wuKrp7O8T^SLfZT$j^c<~WD4#C3t+?HNYCF)=u1^_6qi%s9MGj#_>8Vw|~NokvEjzTUHw=A%41J}f+UL8JLz`t}V8{a@KidDO=v1m8FtZthpFjt&a(U|sZ(Q-W_eOK4qOw*IXCVL$!9ZG2bhl|J)#A;zPw{esp-wZ+f&XPWz!eZGo6t&3vIkI_*<`Bx^zeCn?S3+tlxyg_kmX~n|2O!;hmg6ZGU$E?2o<Co@s)p%mm>ML0p<STcu&rOYgvx(-TjvN}c`rUm8&2=e%Z%BA<bS3f_DEfVov@S-;#X;e@Q@@w0Hw9n!%{A{U75i%`_i0@e+xVK#yR<HbJ)ZGPv@V)0e%DOJ{Jq%cd-@^eneDUX=g$-~|F(Rxpx-Z8*Tp#2f0go6S|O~<l&?89oAXQkV9@Hb(0k_l=I=LT_4S{6XkME7j^KA+Jwx*{&bJN={qF|Syj<5CM}+Y^?o<5T-@h~}^dE7O?<yM@v--x}Nnu`m-_GXaNX|#{CFi5nx1NvLOnyFcUv@rnUv@sy_>%LH#*v(l*-U;uQh&+$$bH%QNaIM(NAAncM~Yu^K2rRW^O5@7&PQIiP=85%NO4N)L+;D!LmFRFACfPr59zs*`jGM_sShbXlKPPHBdHJRxsv*j<|U~QX<m~0km8ZlhZK*bKBRFZ^&!P$tq+TZuZym#mwOM-WQ@02?yrl6TFa*eH~BTC@=uFBDgW-%A~oUvep)PW$MBfD%|zq85c)WHA$T@)2AFFgcs6)3)C0U2><gU-_63JP88`$y2kH-=0}g{az+vFI&;amUa46Ih918Y>27&#+OQ2rhC14-ue6SCA5!4&J2s{gobFjPZa<>ES)(Wi$w}NY-?ciE)3-oDl3%CY)7+eExLgTyxx(B=i+z34aZUk3B_kydy`=Cd``@q%EXTa6qW@rbv8SH}Y2D`xfp@+cx!8@T1;GN($=s|EBxX#^@+%1{$pP|_}heK1q;ou19DsTjN8FV#x88{M}3XTLjp=n?zI10K390iVsrh}uwG0+Tf3^*2=362FXhdu#b4vvFnf#bmO&}?u#c!j&IgsRYNunI0g<6I2Q0vCgepih8{z=hCEa3Qz=ngK2V=R?!M`QSY08gL#s7n%mn1#f|-g13NkpsT?-;LXrg;LYGo&=l|{@J47dcq4cNGzq)`yx!fmLf4^jPJ||b6Tu2}DOdsfqj7dX!@&-405k#|0QQ6~1ABslppoDpuou(`_5#m`MuF#py`j-yZ*VX)1{@5Y1&w9XdnV^a(B*7;U*+rrjbqdMFy|%Ecs9LnbM}L-VAK0N=TJ8N-cOwiocXyC22Fsj1Sf#kLRIiua4EC|{1mhjS^};FZ-*9xw}ZDqi@@8!70^O(1-Kkq04@iYLG!_7;3xU`c@B>t&wu)p==7!W7fSd8sr^o|+_BzS?H=gw;-@&zi`NwHBEW+-_<6jNV1EJUNApt'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
