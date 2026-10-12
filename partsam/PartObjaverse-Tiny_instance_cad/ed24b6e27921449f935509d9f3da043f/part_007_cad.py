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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_007.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_007.stl', 'source_sha256': 'cb242b6398b8fadd5b88b51f2c669bf83fdfff100ea6c9482864796aad5edba7', 'input_faces': 154, 'input_vertices': 117, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.0717807486653328, -0.1640390157699585, -0.0773891881108284], [0.2685561776161194, 0.2701824903488159, 0.07877131551504135]]}
GEOMETRY_BASE85 = 'c$}qJ3s6<p6}_MlQSnzqMKBN10E&tT3dGM7P!KSZiV6tw3_|hCH%4QkSH(ER_(erg$rI7U|0ie^KfD^1h`(ssF|BCP%rvQE89(TlYP9#Py+|O_&UD&0vuCZd?!M>jv(G-~9*B)@*4$Z>pNHmH6!U0qYfV$uMswEYq~+vIOHIq|H#=*doz@<@`ZZwTTjR&XCfI3nwE13B({fXDyh2P~L(+r1d`({InK^kmQ)Z`R=1fgf`lu;0bJGkxH)Bdxn$h+iFkrB+X`qj<=|j{1_-kc^U<$Sz9<E}U7gG(~^<aOc0kx}AK38ph$+fG{Z+v$^>E?q8<<OUY|CK`X-Oz3De^LS6HaP!l`1d?AU14oRz4%{qxT4VFw5b^F1+GWn=R6kU>Jz`kxVDc2pzBw=UsGu6qHkBa-ak$B=}$1O7UWTic<L^Qo^5{t7+b$w>6VhmqI;&E0h-FzKyUR@^t7KYBmQ1<WnN>49fj^T0sh+jM?00S)%7@rc3s#P@V|Mh5PD)?==v*PjBE9)UWexy5#oQwPV)L>^{&cBx?WTTfAdnOLgZ`jGV%XwOX;8fwS_mtfA4k7S06bh5B?5gD&YSj8UFgt7x1^`P89v##Y4~wpMR!w>#-uy{SQezZYJcx*0WUf!e{8m=2E>5{wKPffF2cxbunMvgmp1JIVbwD`cn9}DA|EH@5P>k-sav8jC=HPKKg$)9lGv2<Ph4QPLg`+zeaTb<5E|Hw(P_6fBaGOvK-Wjt-s_`cex|FYZBtIee`rS>f#ggDXG`QFQtCw97djJRzlamd4O^CkueA1f9RFyKU|UejBg!+aWBW6hQ22X^`-|tMZH;f7C_f7zCyp2Nxh|xa~&(8J5(VbwbAJZG0v{Gl`^jq)Q`E1TLG{tU;MWX#Cn?dJ%_)!b(!cN)$Bpr`t@!+KhVww{aGa9u<QvwfcolLAbP@W=(Poj*hkiq{i3hZvA&k`d(gkO{DSBkWAo5HnEW>StGOfk$KJ<*i^4N8?&N?!pdIeC7XD@T-<P^xAbLrw4H(zAx(sdiO``974|St=%`Zkii*AelunhCkuE!n{zh|P?_1%j3MvX4Qd*7~?{g&2S_V3>}7BtrNvq{ixcj{4Z+JF<{pOv%=&ueBcLHy%xioUT*hu^xP*cV!bE9yhL@(Jon3w$~YaTfHDx{3P>(B?Bx_Gy-%==bX3udg3nhIrP-N<Zhb*W>*Y-tf2hREr+yBjZi2*o!<lToiplIL;SKLgWV2OX+3N2giMiegm9$LVy3RjQe5DS;P@mvl07ltNmHb@522rWj=>D4sWDurqY>s??BN)tpD(iqDK_NzxJ+WJM=9*MXz{(I;qW0LS5VX^c6kw$3<wbv*x2cJ`uXUWwFHjBy1Jp-M3Ku_uAq7Fz=a$bH?;px#;V1M0a|C_0?`4mwr-<KS%%d*X6vrd`bMXlGk89Raf!6_Qe(P_xnknKO40I{yq-p&|c|S4!=2Bn=y|LokcGlFL^AoV&9u$yhN|4fWNjQ`uB*dZqPZYtMXHr&(R51w1YxLU;FN9<bQ>nGy3qc($A_TM-j)(3s^VX;dJQc6GLohpG?8`$P_wL{P)k2^Lh8f-B|x`7KlD~^+NQY@lVu6ZOJ0(=Z7+^du@HmCgdX|AG*!547w?-9P4OazD4?Z^A&W>BLekkU05Re>1v!?=5h~wmrduli9Xtfwk;%EzO!e(6aAzO`PFV@pw4ZlJkQHIcEvfN=R_?<o+{^yZh1ZfdTGf##Cv$V=t*-H!*84D=3ajj-FwG=;C4URcd2!vFOcttt&sb4W!oyLtFt&aYP(O6c%6fx>#=#rvlgdYG2d>Z#6RJZtoQs|$eZ<Or07A8mB@RS<ESs&<3#D_<z%d{zH$cE-Lhf1_=j1sAN1%gI{a3|%ROW15!8=vy(Ra7c5~%>oVOnJs<)Ewou1JO=ajZ1y8?a=-Iik=9z7KObUpU7zS+LGiT=SC_?~JVHqVCsqodrz{Qo59Z2KdL$mip5(eE$W3Vab^Mjo!Di>_UcK;68PgK@1j8$_SmYbmg~b3F23x+8k{yDJfAt36pV{}va4Awy-JbLu}pKgrr9=;iOB{<Pw(3Fv2ZYta)co5X4L4i??tV;j&dbqxA@;U?#=_1rkLze>q$qH7slFy86R#b|f#EqeP6xc6w0`z@H?vgx9?jFWTTy%zOoTDe&CgZ?-Nv?ZM^$Xg3PeAl(u?{k0dC$`D0{m-knzC7k&+-wYUG;ZzbQyN{_m8gCV`0uam(*pjxD|=wT|9fRO8!=2YY$(y6ybsZb=ufV&3weKHU&96xI}?4#edw>aH}N;bF60WG$=ev#$*_)wwPm|Ku_L*MVQ(1Lm8jbNXui~Z*$!cxgAEHZEZMMlwT^~`^H~tvzVtT}mG7H|B^mZxwdBOf#3b@$qJ@}5u5b!@GBKVwg<N4Gc|7@eS|Z~fOddo_WbBE2Kb)p`3{CMd#3b@0&PVYm!y*ieW?SKCVgz{%F_;)Z9!~5}^dj$1-iJBt!<_b^?o0FH8Y%2WuCP1#8{}PSihIzyb6vahoqj|w?Ux$x;`(_pz7Se4*CCj5NhU^-CzGcThmog{zfDuTp%xSlAr2!S#`lL1qsfPmt2I!6E87|7N^_y+W>|n>-KeR*?A1{*h;3K;DgGL{LiMvJ@@RqXKy)GZV_#~F<{amBVgPvneO@P;$eR<J5l!UH$Xn1%oSPlFD{&CHyC!?NVQvZ?$rW}WdXhU3ThbJFV$3S0c0?y~C;GIbPdnzd9rcDByD=Yb)cuH_<O)YL%9+9e#1Z5Q1IY&w8`jN*b9JHaP7G|61BE@v751bl9!hj4cjvpI#1Z77<Y6?$dlNm$J(<(qG{rm7967!t<5qlvVWSKiXV@ge-Z3nJ7Dp|WZS`!VVPhNlL^jgm8tKFNO!2qao@Q8vVOit~vx#}+(}<bW)UzB~7T;Gkom#qKX@<=tS2&B9OP<U2Y}!n|qwIIoGB~zs&tU&k4U3Jovv+RxpZ-<%%THIEpvgb(e*I?C>q6r<j~adbe0hkCeogHyW0Tt>5xdmaQu`N>u@E%'

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
