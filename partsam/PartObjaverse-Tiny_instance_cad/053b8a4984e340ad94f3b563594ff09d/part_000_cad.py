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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/053b8a4984e340ad94f3b563594ff09d/part_000.stl', 'relative_path': '053b8a4984e340ad94f3b563594ff09d/part_000.stl', 'source_sha256': 'a0fab4469b4e41d3e3c82f32e46b0f879884942a2f57315ee83a7fd01a503d96', 'input_faces': 495, 'input_vertices': 313, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.0326073057949543, -0.5000002384185791, -0.2043338567018509], [0.12110590934753418, 0.09813964366912842, -0.029548589140176773]]}
GEOMETRY_BASE85 = 'c$}qM2Xs}%);>3cUPKalJ5eB%P(l(CnjAU^^75$ie8>$DDN;iR!2^Qw=+b-w!U-fa`5{0;6CQ`45Sj&$n!piIilB5sDQ{->H`jCK<*oIv|Ib=`ec%0N&z?Oq`_4TD;ydIC4%O%{OtZV3f9q^TP2*NX3)RLXCXE`{H*sX0p~J`fwBkbNe-amV>h?x_PoFkMn;70Nab(}5@J4!glXv36BlPfhh9!+kN*LOESW>@4uD3}TJTj5#BL^f5Ph_8~M@2?O=utHy^hx^v@vjg|!Me7^+Q)J9hX*-o*+T@{<<BnRsP~;AKI`o#2{iBJED%`X*(KpubK^>mhN9~g^KWwN`r(|5x%pdz_vN^CO^M?#QDM7VmvLl#O^G9Q`>xkt#*w=859lra{;|kw=~S9;tpW$cXGOOUCL9*noOJy~cADGYgsz?Ybd@KL;xFT9ioeuN1Nx@QyPCP;Xo?<)Q|#0{5nsQPEwJYrv9DTDukPRQmkbfV;j7a)I{tHFUPe-^7++I#f3siHg?}vckERLT+L=N5D7rc9aF)<NEc$_n`$=&zU#-_ZTA%6AdpAmP>)Ld$zm>B$%cH|TppWl2S?DXG#6CK&{y_PU^XmRNtwsLY2-2N;Nm(BMVO~Apzb9jqh+~AE5&M!}dyUY)Q1n`hw+ekX>HeB~PKrEFf0ZiqU0&TOcbNQxf`^L!Whzqr)NJ#m&^51aJZqWd*3B?I#pC}xk4F#qxB6v>z#0{3{d>Z{g`y|4%5v*w<5yEW{)VDU|BfLEVqPci9u@O_?b}SDzfQV2>FU=)UmkwMtsA#WAMyCNQ*`P7xK|eu2j_s<E12r}fmgRS_TA*xjjo?w^!VTL`a7$7ZFlR=te6~+|1EEvfd6%`e?Z^aq_w*q%!8<_G)2GEit1_|>9QUI{+6Ok|KX%NOK*ww^goQxa_dI?W3m2bo76Aex<07V5syB=s|Vr~7~MknZKUsuy<-;Dt)}RC|Dd{^KfSs8`(>`4NB%Rsx_#*h`D>Z^oAJ*b6TcJf;rVHQ?dWz~H@<#O^>cgTLAS15uX4nrKR(%>>t?q}r$zpEPttyAr-W{l^q=zR1x|VV&5o_bxu+HP`UiA>S|^cb{7f;P6WoH%r2$@Dzp;tVTWvrWk>{TNVqSXkT(O?!hHfK7{AMHQTzz>3<$tdS>D@_p;-E**OyasD$1QQ0&dC_BZdJ)o<EFM7?U|RXpEX|HFY5<-V7}6Styh=+=K7&Rw-)slx;!V%4PM>AIceMoHr?~J3s(C|prY$#OVRpdmNnh$V2&k!?SNOeelJP><$DNSd;Egtzk}+*9zB@+7m+UO#4esPMeNs@--K>FAATq|-F$wP@|?Dg^p1}ye)$oHa?|ye<gcCRIn}++#z6YMn2N3+Mg7n63*CP5-f8#u%T#m=-!J2Sw-1D#e23<>GnVpHbThRgeSfF)61wx4bmLK+@HZ7*%SZn9*5x0G^?Wpr>aX4{aXy$0)(GA3ji<UT__NUMe|DLl+xOQ#*hlDrb2X*D_})3tjZ0lGx^?Z4;y-<-IJb30H=<T<ck9OIpJ%({7|^Xc^@XlYyf1YBA@8^{j-|x;5B<l6LN^;8qU)k+TR+bAd;K(Ofyh(-uHpB~hOYjuIjTQ?*NkV1zx=(s*`NGt6r;L&+I)pT=>F`SQ*PZ<{Pl&q={i>Nm%4T`V}ZLK>^XDA{u+v|Z|YCiM;Ep)@YG?RdBR`M_Uihe0m9#?e{g}je(V!%>3Zto(FN{$^EYWnb=xR@p@_48GMx{RyXbeSG3jQx=rqr`(5<h#rMPuN@z)Qe(zuF$Kwt6Kh3<8;n~X^o>j_=1o78Q^-~V{3s1rx=m%6dFyU?B5Z-~0G=2crQ;;Z_}^>jXOBi(<6;%Li}kD{B$r%?QK(v1~UvfS~duI;%=>$zweo!hEE#x*iXH}fx`bKvgy18&_eJD>LPZ^gfK>)JlrFT2QYIyY4RbFHXel=xP~-{~CMj&(?Xk>(y(hi)&aMfXR~%hI^et?IF9w2pH;y8rFrDY^L@bI+`D$M?%Pje4fI<Csc5GEY+(S38!H<<@1M=HM8buM%JS+e)6&-&XRJ<N9|X{%=orHgn}~D|#T$_jY;e)7(FS)<e;?XE(Nqx?S)E<x}=eah+x)?iasD`a-X+WwaIkHgtP0;;bD@^IPQAt$$q?{{GFGq&KHH&dt3dzNP3|5aN$;X#H`08@OIg^6K(>)oC$ok(k%;>f(I1H$M~St<jQntwp&L!fzJ+ZW}+%UM$8fbDz#(TqhXc+oWHrNpWJvP(465wp0*t^n50rS3Aou5%H%~B)!KesyC@`d0*)E)iA1)HWNM(`kkpl_dnlo(5>rtDpQ`>9qIeJw)0Yv56(kpO*EaWjk+%NeDCg)Zf(vMy83(VynKoLmEU*g>Yim{J#o&PG3SKt-<v6Pd7c|tq&tneuMoPtE*db6t}6=qNyl}R-E_Lpjr*lmihPvoK>zZJq$}5Z#?j=J?mYE~C*r!xOj*0qJufQ`dd@7%lV|c-p&JY5TJCun*`%8@77AUxZgh$-7P@-fs7=VWJo9=OF5)<`j^$nlqj_~2cSzo3v5$pb&~qx>Kl)W2_oq_Va#Anm=I?ConB&$>C60~zO;d>@bxVmOb!`}Q<^IA@ba{W_JWoh=@1s-u0L^!CpJewwIxF`J-O3o~@t5~IhB3(NkNX|tMb}lieSb~p>i5@5og;KRsHK>fh3jWq)p7l-e><1r7be}0`%^>FE!>~#4=$|otPk${{E9B``<$kgR*P|!b3=QLboJcuN46HadfjNMI<5nyu3k^tsxGf5H+K-adj14-<-F2|7fTVkaxO_-J(r9h8Vg-LpG`%V=d;ue<@tl9=z-@CLlP*TVYSY<_g7bS?5};Y4~=__bRG9!j;iDS%L<7|75k-}|2A~>IfL^<?NoQ2*z!5yWv?#pfBj2igsv;k*-TZ(b2F)1%5yeL)#2~27AJH^c}{35x_s^@bxV0pXeqk%w`Y}KE7l>Bo__}BJKL)V?)Td*TkBqDKb|L;sxF^Dlqt7P?7Q+DSn7V|Ik2wy%jdm@;xBdmSP!9V3G}>L$8&7Iq8oUQZApEG_c^w$=z-_hv7ZUu84*O+GjGy!bzRX7JXbf?%~&t$?XxZ7Ii4ZcN73c_=-p-u-N?U{o*QHR4Mh*Ezx|!iO*XX15ARL<itbdP_aIWY&Of^7_BR!O1Mfjh#b4FU^xHY^_^K}BTZ%5@*r$Uxig_vTS+p}=UB1^aq^`VY@k?EK&tfY6f%hqjf8f2zS<=<_EV`lx;`Asibmv|dy6?vGMqAPSc&=y^p0Y{wAN!9}ZhuqJ1O5jxg>ESC-Rw@mTZKQ~(>WLLp03|d+eF^SMu`2gurL3ir>z(FiH@S%l^f7=zcshgh5l|FU2oK&eY6!_$39vI9%Z=eC*ZH>(qGkOp5~1!yT!U)c}V#bY`8Ty{lEE})t0Xn>(=hU9<KZEO`!Jz@#%CQt?J*@%g9xi>vmMz=g!l_ytHFpUCv9@MVxrgTj4A3Hr<zATGO}{)Izm)5?rr@xyb({=Ke}}VD$g$m2h;!nE&r9;leD34$O)I7lRiCU&^c&vvSNLfEB=hXO`EeX)A%BX~dr}%f~(^16OIpBhYs>Fa^9Ov+~Sp0Ly~^!7RUz#^IP3`~b5;jQ<OGN+bRWvn9+10pr1W+bOi4LL28_G5em`X<%U=@j>YOCa^U4G-iKgwg>o6@IByP0lx=7jhJVF)xdi)D}#7t5R3Cp%zS9~p^bCikI(rmcp-d#6S;K)`oQ@d9n90gJ}!YR#+(*ozvcW2qkmy4%fR?WkRQj6;CwFSF&~cM;C$Xcpq(Rc<2)W?l?E1e<*Q*F4P%tS8h(m({1h?2$Jiaw-Vtq_FVm<_gMEY*e8hRZR772JT%i%?HTIH5b;hwMIIrzu8r3Gp;^4e~E%dX{r##xYPYN&<JQ;mz0?UK1#Q3#<<-nI?4v&F6_s96m`4eD1@YNXS4<P?;a9#uRSPonUUJZLx2v`oh5IC<Fjt**v=e7d*t-xB8L(HOxTNG=)3^}AC4~~_6#JN?*K2*kDaL(7N1p07X3(m({gYh`N44w)f9)n{T;uV8WabO8>K8}w4=C}s2`TAADdBoAe{_wS}fc32apL`f240(qkCg*=)eg4MmE#N!gZ-Ms*CV=+`_ro~<yQ}ZJz$xJGf=`EWz8A*1&Fo8jJ_oeHIqnBP2Y#5@8GJqj<NO%x9DF`t_64)4z=PmZ!DZirh*y<aIIk~Yb?|E7Gl2g9f5z+uv!}r4;4|R!4EO^4DSSQzegys@cvWCH_*+=(4}ep_`M-POKhLqi(crP*qhOq$1QzuXKM7uz*Dm8R%tC-8z(c^3fZu{Affw<Sab5<TV^Lsf@S@;+tWe|~0xaMfi*ue!E$+vxHn0SE4aBVl3<a-`wkTjN@CI0mk-$;l1u=F5U@Uk(v_%6OfY)ah$t({r2z(f`A!r|hHqM8mEgD!K{A*^%p&dsb&O<Oq-p=tjd`tSM?K}8zjq?-Ozf#yszOI~)#2ilmPl6A}yuSmU0FOYwn!vK)b$m2-1h5o%EZU-h5#ZmT9)<!(fQMqAzCnHPwr?=UP|PzF?VRUF4HN_x0uM%A<Odc24?<fWV1Do@)NwE{FZfX876ps}AA+_>U=(-^%PkVM6p1>E!kp{*sJ$NAVz55EEe;q1UJ~mS0;~%j0$u`E7j@nM7zeBiULD_~8o)B(HL-Wqfu+GOu{r$4Y%_2k_(f)qG-`i@HqKix<Nu;_6L2ngOJ<eOUI}fS*TdM6!0O<U;Prtuz~eBNSYRFSIIL9zU=(;H_96%v?E3EUz0L<L2!0&(H3T>md^6_W5?Bd*6Xtjk_y{}%a|{Jm(*8VOd4GPM&BMBJ&d)vGHwiK3g7Y@+Qv~=3JQOiU1LuJ!p>GJVB6u{uYxRIN!R1-N>x*M4)Ed|MSuq?q3|yXN`G9%Ax!wRi97lpj;Vf+cl(lKHwt>vDfNz6mfgc6-0zV3V1lSw=2zVxN0C*<&J{afkGkb$s6K1V|b->3k+k*BjXnO-X$HBl>;M?K14LBbBXJ!wW-2mPKzryS``rSq!&UY|NW40TZ4!#XBF93f8-wmIife*m1Al?PwHt-u5<7eP*@XN^UJn$;`F2vml+ycH6{5tS9_*Q0PnPmXez|SM*R^V9ho5*<=Fdh6n+Ajk$z;B}cI&ddA-?w^L8;%pe$AkX}yavw4AIGdVur4^y?I*PVgtoER=Q`NyI*2<MW8X$zw=svCn0HgmhhuB-u^1-}*wnQ~X_#Xg_TVzc;A4#eZUIk6%q_qs;1@8zE5O^}HxP3NFb%vm=H3+e8hBIi*1$I4t-+fBn}Ih0uLG<H&d2%%>-r1U^eWcrA=)3J?H2O=745&G?E&U;4ei&^#`)VAuNSZlcrWnYz}LX{A%{%hFW>`_^V`5?;75?dQQ)uOndo~2_z;|*DdRBCIE=9meR$t2;5F^f^Nn*8I01YB_TzovIB*j_1A+Cxdt;6RfOWw?XZAnLa)5WiH!$1C%mDTSH^7?%6T!2Y-9f)Q=(7Q_?xOuJ+Op9n5#uLfY|hs+o6YP#FprP;I%YGO^#OJUufptgX0HO<fj45-m04q8H}Hncx-g3ab_RciS$nj%M;qs1%-W*8E!ti|pU!CSjJ7be$$kyt7v{>T3a~MFTlAj@oC*FOvsswWEX+a9tsP>tgD&HBL(Fbiiz<l4W4_`e4Du1L!mOB&#^E>%V@_f=nUCWmtm-2!b7~802i_LEJ@9q8Mi_(ltAcSRB5qaWP!&F$w@2Sez{%kEQ3LmYLEwF{N9%#J!S7*?>wq&+J3QVT%!lJkzCY*2<4!{S*%+6%y@dQ;!dl5(gU~MseL3%g{p$<t0{%MoV={1#Yi_f#R<q&H`Nzx_F?-oZ=<^Yu&-emn-GP<CyMy-t>fptFns_M4`*Gxb<|8hTSsbW=_dwr|fs4R-%#zSJmICK}3!*>A0^k}rACKcg<jZX#;w?lh&f`1yf<p8BxBmwA=by=Ad;U|H+SB{0z}>SHyWkDHIEe3%mtTLfi~1mOLzb6ceQN&(RkovI'

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
