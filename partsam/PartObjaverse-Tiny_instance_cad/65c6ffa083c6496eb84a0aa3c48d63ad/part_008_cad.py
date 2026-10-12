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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/65c6ffa083c6496eb84a0aa3c48d63ad/part_008.stl', 'relative_path': '65c6ffa083c6496eb84a0aa3c48d63ad/part_008.stl', 'source_sha256': 'ac659ad4eff397a275765e33fcd7f193b237fa0dd19da901f5dac490b6c9c13a', 'input_faces': 367, 'input_vertices': 265, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.30318817496299744, -0.46167635917663574, -0.35929450392723083], [-0.24848149716854095, -0.1414618194103241, -0.0479603037238121]]}
GEOMETRY_BASE85 = 'c$}r03v^A__QqFU1VyB{TrG#vpr}%Bm5n5VAe1zSIxe9>B#lQe>h`FMtMzPYy&ca=OKGK5Qn87=pF*OP_Oz5}sb>W7xM%M9C1=k&a>uyi|IZk6d_Uh_XYRGvnrp4|5IWGqv##R5rpo8y8~4K-Dn;>(s;g#2#?6QtA343<wAk5h%E$2OuUtPKJYrDjNH;Z0&GnlQIemPbUw4aN&xu|A+F1N1#>CBt8#iriOx%P>@`J`rogV4*r@u8WHq!a;mK{2GYGdixs*Poy<^T9s-Pr|e%%oFCsV_StE|BV5C+8kD`Hnuh=MC*uoNxAZp9?>d+5)2s%)a{Z*f~QJPoFaT*2qz3jXXDRoEG`tEIeaqvtJ5D{@7+kq?Uy-MP}a?{5RwEj`$qmtIV}VKWx7w317c=iu=82o@^fyW;~~(_>{P>cDBFatANsY;b;428SN+Q`$e8F+Zn!nW0`m^Tcd^PhQBFOjDu}hjNw~bwEjlqpV>Xt=x>9p!@^(D)bO>MGvzohj5}fE^ZNBa<|W+lwRJJNxNlOoWJ6~bCX4oo&$AyDC+6Mewc)t&?^my63V+5t!?$%Ao@Vr;K`8g9(Nd#+w8aZ@&Aztrp;15f*^lx?`=g#*SN)b02>+)`M*UclN>7=6$D~<C{aCjArO@o#)?GE~M|-zsk=eIjY{&IewpsYrHWPWCzI-Bl)nqmI<MIvR>))pu{kA3V6}}eS#&}LkA0_?5CWfzT%XbSutt!{g>c;!UedF&L<Ewm|i|5kn`5Sd&J9|xxgBH@t@Er{{CkX$8t0_kNTB8q(@!64Y`0C6mInDtMxK6Zta$fQubA7A{)J6V+b6gK@iOFJo@{$Z+4f#;ayX{d|u9FXLW{UPx8X3MG6T<b=unG6;_`5tm0ZlTD>$@5nzJBo_&*%7F!naN8WB8U9%J8j&uAemWjJm?@TmF$|_VuAlxqag5OyNI>=Kkiyi}u#mzC0e**NyhtqHEkfpsP_o`X^7)&AzRmgW+2S&Cd|+U-aX8`_LxZJM!uqzI|n>Xm81NGkjZ{dZN8nTwG~?Y>l(|x#ni32|sl&w~zcVvoc>>^Ob0?8ZP5J{=0>5oidfjr~fA+k6IYQ?Y~YC?d?Yf@;u&ID(@TFmglAB44G%6kC?BD=l!<Sm}f1bm1wUe{A&1?`$2O2#}sh;$4A6?s@Z8=Uztg=z5g-xZ~Jq5Z4~>b7a8kNe|E0$9S0ZiIpL9#F8qLZ*q`qse68gS_N%tbH2d}z;f8NJc24-J+6Z3%mnNnOzgKJS&&JeL(a&N(&Yw3UOWgN4K40zkJ+eif<=6S#-1C~qW4RE|?L$tai2RE`GkmpbrpTk)Msa=CC=$N)b~vw#Z>Nbo_7^<4y-%&2%6vz!)}p;0|2fxfRL7i3{gHKK`>jKGUwOH$Xm2|=nCq%Z4bk4=caQ7j@9kwCYYErGfVv`&`pC|HL7sSCo5vQzx7U~~pZC#F_Dj=+uT2Z(`}Uk8$L(GX&VOFX`Fg85*ZIosV!reZC;9$|GK8-M<#E0_vt>QZ-NDbj<BX^`y~Q@Zo;F_ATf{=XUfWmJv;X@iE30Q)_RN!&trvY?9Os*vY~<0C_88}k#WRB6hfTF-n0?I>Zus`kw}|%o^gzScy|$&9eYLVT`*+u8iuS)WG<;j%6<NZ6T#xU2^FXTb2c6~hc$Ck{iu|t>@p^0=m2LLR_lNTOEceUzhw}QYXz$7Ax~1*J6C(e<rrf?+fykpDOW<|1U}Ub@w{|?h>oMnAvS{D3C$A&NGU03MyK{TTZjncY9pU{v{etvYe9!Bp{$!b_q$jU0RV3P5+Ocodt)jj9J&Ego_Zr#HX6&oo`(>U6{rH?u94dVK@c=&OKfWycQ+S5!sw7&Br~Y0c*W>6P#CTTJC-#Sme!erE*Tvpv<b3_LIp>*NDE-bBUI!V`vK|&)<omz4RMuORgZmq}Pt==s_aNVY^>$IuR-XjcI-5m3YcFl%_CIYF>qXf%@%866^XH7xFZjNR*Ni&Xh8@Z<`?mg9_<d^1BGKMvJ8Afilo4rW-&&Z>?RWi_Y4)|ToA`Zohw9nFPgu+A(XCsm$P*sQ`LWMe+;>I@uTz{07483Zo!7-ll`GosxN7+J_X1Ct{qpnIvTJs-=nu|c6`v&XsBX7;ef`6lC-Pt9bJJqIa$Mw@KaS7Gw3)(JcgFJinsQX+Q5hM$zPdaWzQc`ud#3>+kL~^Te6GEISG3m>U*`4ovnKnqY8|hm#_tK=;m)6b)v<JWUwbuPUoGE|&+F^WpC{M;ET0Sezax6S98c{3dTgo~PyOfGye_Ie5c8;#pW*ixLH=UC)S11U59hCIJmXn${#N+;R@TK{qTbZC2-e>^iF#A}+VKAIYq+Rq-J>Pz@nTWWdUszQr{sfjy{xFoc{=mwc<aD*od3u}USDI~bIrbO_CMJ_&@NB-L;mFY+{F1R^2`b0_itry3tw;lsZm$jrM<$}W}fG|$~rCc6g|)N^HHwwEh$#shr<rY_I~?$UY1Oi_YJMeelU-RW?#+y59`7EK*#kNX5Svyh4+C=JJUt`Wi5Cgc;P^r@Z+2E`Chan)9mX@%6Ogjo}Oj)RrGy6mnY<=ntiKp67K`MN>fCCN)B`Tl)l+!-!d=8@U_F9IU<jBD!;F;s);;WcpbxcY~Of7^wYgI=lNoT%%kt(`8xGnuIPV<oxDHHYbEm7)^+6lXKzljxNi;q{HQ$}CGuFi9p?Fs-dL%xzx{>CqkJ{~e7AG8Xs-|O=kHPCx6AhUd{q9uP(}N%Qh7i5F;?WU3>(h=`uZ||@-TjX`%P2vy!QFO^ZsyQoA9+e#k`+f+A79Ve_<IuXFL(}sO5gZenbyB@5_5}{^W<kcf8$$&+*t`k;nFv8@F#BE9%Yu@G;-NUzVsh`?)jx+~uEh%lldWy<++2-17VWa6G@V^`hTR;_D-J@b@>b<r@2h`pk>Z$MY*Q%)TYrjrWu8`$T(f>Mh<+Ud&4~`xX1l>F7++eqko>GnSw%(f+M8uIFbTr;7d@TE*)k>{a30#;@RYihZ~u|Cs)~?&f?ae47@;>$Km}6p<h2uPv<PglLcRS6dvABgUcqN?tFShlQ_iUCwz*mxw&pwJrGl@QqHwSJj(ye(c*7{a^kKua{b{RPOhwC-WQ$;C(o#m1yrM>C5ZOyS8Yr%_-#b_uy+X&w<nIuk{vr?D1209j!_b&#N_>%<C>`fyh&SzB^Ww$@>nh%6U5Um*dv=0M~!-ujM@c$>)M?<6<#ijw_RS-Qj&*#k^!q;`0LU11tL9r~|k6=qu_?J#ELIkMBJYdGxXx>?h=ldR7g*`F+UESW(aFSZRJ`>qXmfm)G5%z3E3o#ji49(YHQLsG}4`HC0zl9B2AThD`b^*UEpAiF);a`bnl^=Pv)>pJZN8^wW`2HJs7X89vVNb4GLMGYI0^P#<s`XV7E6gx9`=Yd+v-p>@ISoKfEyFXOc@<62$tU!e8Dt)1cPjJ9}fTU@ITt_Sr6zvzrw&S-_#w!$@Ea2;qZa5HDnZ&EGr+7`H03tSUg9c*!iw=u>1+NQWx9b66S4Q}j=D$Zzv*EYd5Z*Wy;74UP;@N~xWc<uAJRt4+@^#uRb8Sc(#gx5C0HBYby)E(SF@n1u{wjr*$gWaGC{Him0Iioj%_!VeRFll!%X;<)T(2fY=9th%Y2;wf#u3*g>ot)7D+6PP;2o7>aXJ-UM1Hb{e9*iI!fFSM<4Fr?+1JixmJHsFS_ea0{;lF}$Angln4-SBKfVKy>M_%F~c*bGS?%-kI*Ac{F(4OEh@EZu?k<eb?UYN6y2;$Mu-r&*TG0?u?F<`6dd8`QHanR1-ao`EiAn*imBs3WO7BmVP3=YQJ5Ko0hLkEDTL8m|mfCpgSh$llQLHmRIV}6MzLdQe<fk^|we}j&N27*cZfJr-n$AaI4YT!4)5m0|{1bCEk)!8TnaX7RiI2=3z+5<cSJRI5$JRCd}K^zM00uBWaLJ)^IV<2=ev<sNDE0}Z$crdsaL3|ZD415)Q4f;Cx8u&Ui4167Y6Z!`DCioU~B={EiE_5{bF1Q3b23!Izg<8R-;D^w0;D_Kc=mc;X_z5%;`~>_|x$6EYg4o@SH402Y?BV8G1H=@>RiM#e3gW76uC+l-LF^5k0;VALa&xT{VhUnU=p--&v74J~%@9)%E9iJI1@U9$T0f5w#E+n3!H>WXpl^a7fbT;i!1uxTprgR|z;~eG;5*>k&=KI<;2Y54;2YpSp+mucg8zVqg8u;j4jlyk9ef2E0=@#itXymCGJ^Ow=wL8uG5CZtjw#prItHKgIQTd4WoWV~e=_b*nriA#D*8*BX6k<$o{u!s^t_oE57I2t_+(-HNOMi&nTzoz%`=UE9_EL%z%*Y4m`~EvrujXM`6n$@u6iJT0R2I^>WBCd^sI8#8}Vc4dF854Vya)#3t$RjH>g9o>YvyX`ipX{7h*5yCFNRQ#NN=0%C#Pet3rQOuJub?1^Tmct#@J%=ugVEKM=b^e^jphg!n1EbIP^<5I=#QQLg=pxC~mPT>BgGL+B~x+7F3Kp(mAV|0FJf<}25JOMDlaqg?wl@hxb!a_#5DH=!BIwf_@eho&pnc|m*)nxb6i3-MLx2{36fc$PEXamEJd9PkG4W(4sT=v*-AKfqhS+YrRtq3?l7=YzL{cOr;)L;ndTT?pO{jz<vhf&L3jx&*ujyca>dAG#Dwx(vJ@{1t*Y0lE@Qx(b{C{suw(E%YNW=?d_--~$Nauc6Dqq#uI62Jb@<e+m5nOu88SCHM;j@#oM*VA2KP&%vJ|h<8EX2b0>syTCgT#9N{Bz@+bjw}R~m;!V)mVA8*XH-R@Ih}S`9f=Oq9*MZj}h}S^h29w5u*ML_eh(CtLfJx)PAA>(Z5Pu4t4kn!i{uI0(x&gc%d=NqW9dtAJJMbas7VshPVdysSVQ?aJJ2(;iJ#;7dd+-tHZtxLs5;Pv11U?Gg13n7Yoe?_F&AqP2fBSE^u0I={C*nWl{^u*@S4HMme&Wnk@x@W-Kri|Z!1+Pl-I&;g^sS2eHzMM}Tm'

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
