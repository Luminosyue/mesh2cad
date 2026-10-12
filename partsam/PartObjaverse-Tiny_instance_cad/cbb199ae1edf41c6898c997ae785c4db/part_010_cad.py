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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_010.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_010.stl', 'source_sha256': 'a4e32b82548c2f0551b76d1451abab433871ea0d072071341c7a1fcf6fa08f58', 'input_faces': 192, 'input_vertices': 236, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[0.46877774596214294, -0.2445942461490631, -0.07710760831832886], [0.47083398699760437, -0.12169258296489716, 0.07710692286491394]]}
GEOMETRY_BASE85 = 'c$}qLdw7m@7=Aa0s2r-%IWMW9mCOifTf{WdN|L0$k4-6|ZMHV2&-u`dZG;{2VGi4DPHCmI$sq|zM8o<jg#PHC=;{yYdF_7QzTflvbzNQcUDtix_ipzd@AaA6Z6x%sS3k_Ed$qP29pBl--_o)i+-QYaX-UbcqemvCJT!KEMu^q?n(w@r^9BxnDq(1dm1a#0PfSV~nH=834(~atTX=*WK5ATYYO;6iE8~(AlN`UVcT7qW`6;h?$0yOp?IJsOjj%hnkFY1(|M7J_J%T6Is*NFzJw5QND(B;8cWkW+@-6t)QK^4M2l>^f>U>|^j;%34zHibEb-uX6esyJ};(OqGE|+aF`Tk+8jlM5Gf3wN2zS_*_d!pxUGWmAgm5nApu>02v<NfTKa^rK}cyNR9{_)B(lOOwBX{pJ#jue&{?-$NlZ+xEHGuIjKpGjP6e4Y_Q))?=UM6C|?WBGk(tp2*Yev1~~7=!OAygc6I+x`3*Cg0bw;WXo&2E%3<?=;PsXY#ExXBU|K>ff8>n0)_;Zh6K#uMS#b%paM&G}yQK{_$nYO@3_eT?NK`Ty2rjAMnQtlOH&F(@K-?dAZdplW#AMT5Zg?>{V>c4;Zq><ogdLt~KWCXRb5mXU|!0%zsi?V$4UEmKyUrE6a@e%Lg_X^BFbe#(c%E6~=t0D;tgPPv?1?Oup~8W}A)qh51I`pU`?suy1i*^rYXasJiy`Hc0JB_G3ScH2MM2lkD3swKn=zf!dSqeXF_A4~U**-_uX+Ngw~bd)1y~-&&;hB>RCTYEQE7IidC>`@X?yPqH8TjoOp${UWs|-RHSe?Me6kS+ytK=NYN?q<g1K^d$S<*VUfn`=O#I;aBI1p5%PA=t=ng4x%SHZ>c?L^ZV0S?Me3S@711k^Ow|~bn_myC)xKUsy*rE4~w4U`^Q92^7{}gdXn>fL{G9GFM5*SpBmAV{5-?ep0xPuBv<W8_U#sGPrCVdwI|v498`PK&4;Qz>E>stJ?ZARt3B!FA5(kM%~z>C>E<t~J?ZAt)t+?o<!Vm`u9ny3JE}eD`jKi+vTuo=bo1HyM&A}a>E`>2JsA^j>`5EG-Bta4R~;R$+zGU8W8Amw%YDnf+_&t@eJg$5x9rP(D}CO#(&v3Eecrd)ee|~UdEZK(_pNpx`&N5S>|5<V_O0}J-%6kNt#%*#R(l@oTkSsft@b?Fx7z)PUd6`y*uC!83BRA?T6#@B?_tfy9@g$)4@;l-u=IHkYj?1RwL93u(&s%aecr>;=RK_5!5-G~*u(70JuH3R!&)ADSo5)mrO$g<`n-pw&wE(QV-IV2>|yEi9@g^M!&)ADSj%G%YkBNpEss5{<*|pgJod1b#~#-5*u&cUgFP&L-osiRdszE<(erNKiapG}+{4o6JuLlz=vBFgwfhBXugX2F-50$o_psalVh>B7_ptPN4@;l-u=IHkOP}|!cE3pNRk???`)Ac&m3vsb|Df8dawogJ!FzAI=vA?wrO*3WyOS$=RqSW!^M2OymfEXwKTDtYvzEW4_Nv^^(&zoG<qwNq75iEGyq~pvAJMB~KTDtYv-Uj0)n1kRS^B)6wS2tVt8zbU`B1f2<$l)k+tpr``&r9Zsl6)qvzAX+dsXgd_T_%o{7AJ|<$l)k+4)A_7QHI>v-|r|>}U7aSL|nZ_Xh9h1m(Ni-l;2Ue2wWOp|KTajq(P4YuhoM7qj_W+oPlY)wi}gb&veN-`bu}&#;To0z3eE9^o^>eDE&lTL|%lIpAvOxrCjBFmQk9ImpZf?}WaI(2p<+{3-Nog7d!K41N-N7BaKJRnW}{eF-zbpFqzf>>xA;$3f3PW+r$CbQ8i8glXXI(9;PY6PkkiKu<$vI{0Jg8wkA!Q^6lX`v@Od&Odk5ac}6U$oRk?K|5a_v4qLs51^+IDhbzvABUcd%oK1X^mPR1>vkgeedtMqZG=YP80d+}OagC%Zb0Zs$N+DF&LnIlGz32eoq<dycq?>0LJvYZcoX#7gw2Hd;76g;k$D@u8QS@mp{EF0;62a_2zv>)f(JssL)eYX?x1`Y^aAi+=-UWS6SBddLoX!kBis&7fX+r{A$TA39fW5Hi@;w%=MeT2?gT#zy$G2c@P6nt!bU<UxI1(zVS@Gd%h4g=H0U&BL-78$#QT~KorRlOxSIvPJMO3BUOIkk0+5B<{P~VPPxyr}9-IQb3GZ(YU{BDm+j;2o$U6EhLNeh3;OL9Ec@cLn!cW2d3%GXyKeh+Bh}-=6j=qa9h>#2Z5;~7?fN(eXIp|zu^1uh6?;#8(ECwHhUP3rTXa#;AdNDFfz=xo1!Vto{;IE*U5)NC=A1ihI0`$AcECnBiZbKMKSO)$YdO6_;;a>2I(94in4n6|imN1Nv5B>(afN+#>ANVEcd}Ip1N1^X03?~$Vk3km^z9oc%UxqG3rU?8kbUVT;g!jP5p;r)25ZZ%1(C;C$0(=6x1Ho%Ke?O_?@1R!_Y6uU2M?m|LSqZLzjv$OAtOB2eUQIYfco3Wjy$YGt;8V~K5t0bS;M34+2(^Tc;8D=U$gBa^LO)D+m9Q54J@h(4fY1s28uVIZ)`0`ik%ZBN_23_%O9(#_I)h(_UXM%(_($j{!W)EA@K4ZXgfoOL;4#pp$drN4KzAj)N!S2B3tdh)M|cE07J36R<=}JB-3a3d72uzt6Z(gQhSmG0|C;dk%jcA*@*frCXR5O=_%mzimOBCy`ZsX?e567Sy;gF|ZRexE0AGn3t^'

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
