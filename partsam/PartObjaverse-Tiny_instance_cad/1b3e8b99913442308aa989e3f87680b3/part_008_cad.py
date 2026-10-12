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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b3e8b99913442308aa989e3f87680b3/part_008.stl', 'relative_path': '1b3e8b99913442308aa989e3f87680b3/part_008.stl', 'source_sha256': '1c84f1af5a01b4ebe1d0d7be7337158b8a6ace3f8476d8c0ec94a93e834f8fde', 'input_faces': 225, 'input_vertices': 152, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.37612414360046387, -0.35407131910324097, -0.40764984488487244], [0.3639674186706543, 0.14771205186843872, 0.3257004916667938]]}
GEOMETRY_BASE85 = 'c$}q~3v^9a8pn@N&s03pP*e{ZiBcpYB9v2=XoO6}TdA8$;t?WEf*`3Qf_Nq*!iq<4t0>|X5fsU#-r^CDqSMDMs_l4`4p}v&=IsCXSInAOYu3zN>s$Zd`TOoZ`|SPgz0Z~K(2AAZHTg8rZe_ZqJ8Ej03Rlftn;4ytG<rmIV(Ym0$rZF(@YUyuW{36f9X_~%Hc^}E6&0O0BEc(A_v#!I;MGd^iW#4fln@y=e0)MwwDN-^$0kNwe&VRe_-O0e+o!#6E4^KdR(h)bKYpsKKE&3!RHC}{N6=xV&PrbtcD2;}b=XC9tz9;^KsPtqrhM&o)R)LhTzgEZe)iHXrRF=kFCcGkc^<y+`7j^)XcK%hv+_=S?{d*zT-VUy>vJBQQ)<hN-v-~K$9c44i|&v6%`osiE#bjg=%qQkl<)8yyBX~-=>y-KwQvvezpt_h{&r8vFSx!P`6Wp^<T?Dxkl(z=PUYJN7Z>3=@6H+gyXU?QxPDL_d0OQk;XCZ*rAqB7bxy($JP+SkabEh{IrIed@m^`Cw7&y-Wwo?(cFAdIW9Jg|=hJ$U*Ssd$)jQfTu8w(ij=)bpctY+s^C0>&@r2x`PuJtPF29Fy*T3H^{-x^hwfy&XsP>%)_DMgD7|fHl^8Ixf=T^Dr<T-o8H#7Xuj-$d~rJZ$sjzZmY=A)hc%_TqM2>NCF<^?>L^M??b?|y~S-(HU}FSbut;d!(UQ^X(tU=8%pKct-+1K}GxckDxZk!z)$?;|At;k`7>OJ0%W&-Fh9-Lv`=^k>3F@$c@#xM<nAr!Y>NPGS7Ckj64zV|_8d=3yVHgKh4TAMr33<3Bh>+L_t)3yh=gBmL-cQ~YEX_}c1DvMvsull8Ew!2#&*RiC4saX~V_kM8Y<?x-#E?siD>3%0^HIKOu1-(=o1yd}SFUF6%m%B26h!Z06Nj(>@)r)5~5+O=s|2lgU=<l7$>itpN7)=lH%yYU=(pNT)9Y%AuqGz{Zs-aB>~{ss-c_HFe~(680zIjoz2d|Brn>2`c?<u>}M;ve@w-D<xtl71ErgKu`N@j3dFSuXdjRJsv5=<yWPLt4Ojd~a8#_yI#U;dw^|O8)%2SZ|u6R<O#`b0^EV#rIebEg!rB^>FOA+_%wU)Uoz^EZWgmWlB3=`>#cRQZ{0}>s_2@ao>J*r2h14NvNMaL#6%vJ9vIG;12c;=O_=!uj-SBe=p10kNNfPSO$OVksS1!^QgroN}Xh7XQQ3KpAMkjc27Hl{NLOcVSHIvwt{r|o_RF`>XL%zwjCQO<75AA2K<JXv2Ja@czlKHGcTt>`_I65*oNgvzTq|<_kFQ0>clzky3B9<yj1u;<FOvK$77`a+b*31zjAl%4~{DyQty`x%&WQSZXw1qWQnx@PRug+#UG3RlSBNl57)xKz;zRyFTUov4tg|jHvB3@;%Bw~40Uj#8}gmOm+1ShM?V^@$G8{`n@GJaz6jr}KU4PIL4K0&{q2Tl^X<EON`CH)jmXcQCHry5VUq6>wH1C~@7<`MlYX-9j%TAj%qk;r&e?l@B;(V)JN66BW8xb0cT1VHzq1JbpY#6FV_EOP7sSu_3j3yG!C;<S`7-VsmKVT3utECsW(xYD#TVwI|BmmZy`MgU?+orD`^vf~spo;qu)i4JJwzQE&0m$es(%2!KDjFPJx2>KsppHc<oqjamW6Q&S|;^5Z{c2Cugi7dxhG$fb`qBFgRZ(O_bIt1b$&mg__=W&wp`Xl{(}<a-I{}aR1Z(XbD5<vXxFHBRmT6uMvR+zYVINE=-=i1P3|lE>6+8<wHqt9O1(^%eL1J<k!Q!*ao0u8r(0g|wO)5jwBN74v>(~_h|FUN_A{sJC*sc?BKh9w*%+rE<E5Rtqa{Bg2;-?GcRq=0+fvDYv>)vljtpsMSGoAf5vXUIYgO^9Haq&<_#6n5aVvZuzS-m;#!0Jm<P@$u&V;X})-J|#oye2A>Q@He2+YJeXg`!De%Bu)KW)Wwe7{v|8Gn~wr2UPds4xB649uhX_dDVT)JFZ8`2je8&Ev_(r0z~{M*F?vr2g|$#E<_m2lemU4DFkH*TZ*46v+G0wY_rRlM{~Pe$9$y9P3Pzer`Mr-;wh*&N0WkhJ0_u75L6CeXx(&A9TQd%`Ns5m|xdC)VXclL%Hvj68Of^U(t^3%3Zl{g&ikl9R=gP(=56z?`8KdV_ct{r{?B8@;qfBr;+D7YM<26Evd8NEv4R@7GeJ|QXb;`Fe1i?-@PU3U%Pqsu+;N7@dq4}{!H?~{5rOLaOT<iG(&I7d#|1X-x(HyeZ<&50{u2lt`nd8q-l3YJ7%v!nK#!m+}AArUDn^ChvMIV3-5i#)a|%7Y7dn9`gwQ()aEaBQ!uXV*>P~xei`SFqj#3vrw#YB*Zr~nP48^Ucl4F_?U!atJ+7@K;~iCk_2O*jR*L-3>x+N0TPCjan!|VO^E~_9I3)kP5Oq}^3*QmdM&4`MufaSULpDk~sj>22XsayyT%FSA+v#<Dwbau~QeT=`R;;eCwwC(1-9px1SS@MauN}tOu{eSGX+2S=C&ox!u1SJ#5ATHgIilB=N<FL;e_jX7mwvq-=H2MFS=uR1#e0Qw{&#4{n7&>71-ba$qBVU5{n2LL7ytSP$k%4LB43NEDEs{m9p{pB)yEF0Pw|aQ<yi0f)rQD7{o2FV8*7*sW9=inPiPL=UyYDByw~e3w@IDfSaJb+I|BW8KHh<I%yA=M{8k(AeyC5cVwd?Thi^1EiMlc~`r<vt_}1%7<OiLS_rNQgcgsA#b`kAeKaKV7C@4VvXk9|Z|0Y)6OGgdg(>46LU%$~cvf8`Wu--_msAm28jfs5br>`>A=ZXINpT490{;Qw9zP|1M-=DtfS$wQ$Y(-saBdQO%p%orhyh?3EZp55d8H!sm6t|`Nk=v5nP<_d5$lla9$lm1UR(MjIF%)}I-ykb}lk7!q!BE_Z8bMato7{=q(TWb#Uew;?UgUQfibqi+$fL+{48`N9;bf(MA&(=EW+;A-+Lx@fC;2_{5QgHx48<YTuH+DM7iwd27jn~Q=DsOIaeZnva(%M;zmlrdD%5J^iqy)~YUIjfH)>t7(ne&Z9%MIi4TfTOYD2Qpm&r<BBD<68FcjCLHXtkYBr9!3u19V{^&%^6K~~y{+=ToJwIlfzvaUU?C!P8lStq|ptwmP)0{KO<3soblPX)3Ixe~P^xgy8C64j0D#xbqLP+XJhPIl+m)uh%V*Cf}bHX%3RGuLJ)cBSfMozLS+bs@X3AFkAz<V9A@v0^H9GFj<(@>KFzhT?(LDDpt^Fe_}-XlfKWnjB9ZPmU)~q)sMJB+sVKA<rhyw_>^#rWIqX7)p(yn&cSrNQUARhT;tBbh6S}<P7ox>OArSawc^?c|QA=$xxh2T|`c|BFBnp48>Ut#fz!A<i+H<)J5dE<YekpaxyuVI+i?^^AyWaJjjZ7sNJap$=%6sSrKZ*+g3y}6o*kelRGmvj5?64bQn2|9H~96l}PGP@=(s%lY7PR{xO`tP=@0ER`jEeppGPu<Q$J+D4t+Nk`*6Xv5-1}Jb^h2sTt&j<R#Pv<R#>#)J$?F=V>WJaW*xFtTdgRO`f62*`#zFHC=mpekqQlPSc*AeTvn2_%3x4bsAY|7I_jmjiGoZbuoD+Ih8t>oJvlhCX<!Mk`u`9GZYV?4kACPxd9BtJs66E7>a|b-O0h^Zq&EP-N**DGua>qTJbuyCABkI>D%O%<kr+sa%*xshT`_r{^a&#f9+{q`ZE*<FckNpjv)6T52sEb4<{#5KO`rTr%;o~Q^+4^@~)zE2sMcu9$LZ0z2blRGt$$KsSdj5{;2e?-+cZR{Mm2*VYT(=3we0x3+imN4j~tGBuKp(X#WJ^!nZ#'

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
