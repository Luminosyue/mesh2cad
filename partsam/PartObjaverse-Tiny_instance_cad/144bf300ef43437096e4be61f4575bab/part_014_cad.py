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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_014.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_014.stl', 'source_sha256': '4a7cb8ede87cb91d64c45d6f61a01a1e734ee4c10cda27e81666040bb5a0943d', 'input_faces': 240, 'input_vertices': 275, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3328556716442108, -0.1822034865617752, 0.15213248133659363], [0.03304268419742584, -0.050018467009067535, 0.47181159257888794]]}
GEOMETRY_BASE85 = 'c$}qL30RHk+kYxdS&Nk2!H|q4dzk8&Mn;9~5;{?~%9d&@al#PUmnddBB1?rVr4X;Au?r=;BYTz!5n1N{KKJjQ@0<Cq?|)tY>-)}i-Pe7;zxRIc=iZ+Cc~2)V53>r^0-q*g$)~R0{Zvl~NmYfl2n(1#W8&C=khYVj&NLC0gv-xgd~LrWeZ9O*M3|Uu=N}L<cDh}6jotU-9PL_b?8Z%*K4ZGyWZx;%{R1TK<`)zapyDAD{H6w|*DX7A?c7?^(Z01NLi2z8R90OuM)oZ@E`8~|JzH|EeTTa)DpwA^%$L{tvF67m*XZ8fmbhkjI^nwbNW%5g!U;FlNd;c~=or~cse6a?2gDODD$U3u`|IkFzP585;mRIsg`Nu=1p9$e&@V7QLA>?|!gWLE6K-7VdxX|Kf8rL|Nu5WyW{nBfy;efFaxN71XRpYh=R)TbZY&uHKO4A_{~{ob>?^Z?YyUh3{osDk?+9Ge-#H8Mt|44E&I|UhT{=Y1C4Nu1CZZqw51j%3>slkO?H<t2Eg}DnD?&)$Fv|_=rYB|+U(=g#y^k~U|L5ra^xP_6*w5$!yvi%&fAMPgAJ>_1L)HfJQ{z4X`T5cw{_I(qM!3H<{BPudb(`%yO7?FI0RF5U{Is+^NcV>{hM#j<A#amjP`&ht>rj`aE#Oa_JMuPMAa8wvixX|hA7hIE_-Wc4`j6jJyh@lY{G8ti`0(z?=hLE_gs*D|e|jYxAUlqqfUm9({~b%H?)r{{khcgc^vRwD6tCWJm-LN?E#Ob1nMq_X=qT)@R)QV#O!8Bg(F1YW0XH-_NcqwKULA2Y0<O=fNO{ouM55o82-q24i|VU5*CIQH17EJ9pFUDPMc-w#uBLlA;mU)2%A2q}LAZYW2f{UTeW-s7XZs*;CGUVo=2L!@cFFMnmr}xocun~+Ja<JtP2Uo(i|(0$zP$?k$g8XHe+2rfOE~iLO)>DCQK^K#(8Hgm&tRuK@-W4heVlNSUWB-M_|V+YrxhU&MfZXG>d7BvB=^sH;6fQgby0!?kOznBgliM-BcI<VqR;ymB3{=g<foWBg7lTI1@P0=2lX9_eX6?;T)FK}{%dpmNMCm%k8nfNH>hK?2c$3d05@KlPWjOq<56F$OISB)0s7E(Ir^&n4Avd81^d_X6!KYe5^<FcM?WWTg#9Vmz`Lbnqh7IyYnuXpihW356A_F$`W}V<+IyI{rm3(WcnEfSX;GJO1L`HxU?<1}d9bL1JY3$7d|q(R!oJBw{s-(~KgUoWG@e^|9;TqadUxtK<E&u#IX4-2PF>8g*c#BUv<r4FE5IXX0Jq)_|Cel~cr}xgkhiRD$mis*luyk$%o*c?t;pw!-iRwG67@Zr0R4MAF%QGXqpvbHA+8B8)5*^V9bx}cEb3UAfcc-i4e^$&fuAvU=<}ZY(6{eb!j8ueWM4O@A=Z7o1o}5q;s3<u$iu`1(62p?@@6>AbGTR!+;MOU#ZgdlgY28nft|_+XkEkdwb(~HW+Pt9-82W3EqBnLHZ!5`I~a5L><+SHO!*o0_0K|{BU&JDd&6Pp+bHa7`<m#t#8CJXZbs|sH(n<@nt0&)(irT!^}vk}Lr||~QB)WG!q4Q7Az~`<lyb_0&e8>aSQoemTSWfoy|U1^7Qyhds5{LE-H=kO`|EhrMcbZmeV`@kWi<x&Z$2aYhRAEkzn35UTvf1-xL+FbnXN-y?q*o`j1&5yt1s+qv!b}f=5*vUeiZuWxxl`=V+#F&!1Yi42p8**Vg7U-20vG9LA>31Azp|6i1$@(>Nkz;R`}D<6LwPjA#dKv*J<51&RBPO4eBes727`!T-PBGbv!-=elB)G-d0$^pHAq1!$jcP^+l8i?c&d<S8zAzdnBDC`$x*r&y5}7=cE_V51mT>D6`rjKfmRYzEI$gp=E2>i5X7)X3UsP_LXWa5tm6C?Bt_QM6VXGe<2b3_tbR6t2Bpxuc;K5Htq%bJg^DYwOENdR&XPIeOd$9DO!#5QP&c2Mb?L%)A`6lm<jT~(*|{U<%##w@x{pJnQE|;>5aPU>msf|#+SXzK%Y;BKiZ1Or&A{7K{xsa>=cw;p?Gc$!`wTu33IjVJ>j}JrRcYoDX7<PrGzV=R+1gVc^&$8)N{i1)1IU5g}q>Z#1q1``>&IqT9bzquWr*F!VR8XPLY1XT<oKsx1e8f^Dc^G$Q8<)Xps+ptj$pOHSfrd{zV@AZ@Q3h?Ma;Dy85SqpJ@mCR(Rh~3Nm3o_ABgMsE+)sOeb74dy_+Xi131)qX)3=+;W_c6Q+<q+EsfI@9A*TS2lEk{>3D$TlGHa>)N&<edGI`(BE7@`$(tXT}bOTU59**D1|>+%~8kvHSlxsaqP!{M2gqYd<E=We~I~Q))aX=wG{Z2R_M>z`DEW13*6{fO!k$##h6P8OMu_<#{5a2gZ`hl2zES9qCYP=!~U3Gpnrh#b}<)qjGl}9v@9ikgX>e&#W4tWA_8;CPDusWNeo1ugMLJxJ2@gQ>q*eR@gDtYC<Oj&0`jnLKl<PKIM(eq26&ZUNZ(j81N*2YaLv%u@G}&7(;pjzJiEAK9)|yleLc?${#QuC{{8$B^<C%&KW(g#ht_*w=b0<)^z3*9akL<P!%i3I*QrGBd*XHi<zF+^8FBf}#(udH4LhrQz|IRd%%$qX;eT#h><hm~<fk#z27U(F!%qB5>Nl<JWY}rg0(o#~hy3gwi~KyOhk7+>Li(CCC)9UTUD&sFrMV;qHG`e%z(vgqIDex*lK)DgE!Lf*r~D`;v55DwCGu8!8~L=chn<yGk^dz+yaz_Syhe6(Rba;)?}5VR1Lm_^W#Gwe5brFUBieim_*r>9-v2K)C;QrXQ>=ULG2U<Qu$`x$FC#xuw7&$;bN%OX!VSY$qyJl#W1bWM*VN9TI%?v>5buRj!nGqi;k}~wJ^0_@4eSqFM7YNNDfV^VYr@5$-I#l>zmvYG{Q&FkvZHl1U$^1BIB*T?M&E;<Zm#fi5^$|@1N-Ql6Zxa9RzSG!LPPBLo9A(k{BZ?#uHJy3_YTmy+E00eEAw&AYVvcSKR6foH`!EQ;n^1PI-NpX-#5lS8hr@)cRC4w7M`N_7GuUT<iRc*`d=U6eda+p^zR*oeY;G&XBNK2eDgU1{k%cw&*Wg#>xT@)b-y3^Z*YX4hOWSsyq4$_2W#ZnG8Oox-|)SlW(4M&T?+CLyaah`GK2gy{ILaf*?JrM%XbFW?E_q!br|+n3c@wLV&G2`J-#0;b_ZU6DeCyP4aKW@@Ga`=J|A&?*orwb$_Dm7M`GQ=hL|ThZ{#^99P2)`#@}tMZII8fY0!UVjs7olfgSS+gd3e~s85t9p~z3p804YnCY*QUTA{x0M<NepRS<8b&FCLDAK3qP2lnaS)~MID0l>opFqd9GLcPv-ArIfVV9xaULbxdGgLN$f$sdF8fSsPbq3^H;`^#Y|>aw5%;@$0u{Z$41psa0&xKj6#eX%wXenz#0|2_k#zJ|aH(6?>{J8yR59B*F?yp0X=|K&Ztch@-$Kik(py`GPub+vh!h-+3w*k5mtxK4F|pI0it|A_54_irn(zeQl(<T*Hx%+sOY4!EL}(f4%2l_dBd@;Q&5uj-EZ**FDw-;acAI()@@LWjlh)ATL$qav^`EFPh+LP`kN`S(D6I@W@n39ks(&yK_2J^sY`u4_<CxZ*vL&RN~|IQW0jh;?&*COi6@0=WMj*x8kWx#6CS{Fq+IL!Mpm-m+mR{2ZSReEUc2(>Dv@&#dFXy{(bA&c48Hf$L3us9xITjeu9)OSmCs0{YOZ2Jo{<gp1U{q%RJ&f}gK;A+Fr!$Xjb?oTt0vkhfL=gzI{=fqv)pST`;c>o)yD`80M}3p-X;w11T#cf>Vy1@v!yLO*DEzWqE0`YzWo-%dFoKUXKhf8YMtce(bMx4FQTjg@F!P5(iJ>s$LHuBI;uSL&`neU%ZgGi~7SWar%_;9=gdbNLR=>%5M@FAql@^Jn6G*;Ise_x6VVhbQP0^9<;J2iy?l2mcr3V;;KxfWGSVfc!CBPk^299;oBJugF`SFyIN@kmvb$AJz>u1>V06@)qQb{hrjHaNU!ph&LVjnql*>Zp~WI_dJb0wDX02+1E?-{EH-7S9iKH;hLVn_1&w(pX0j<$d36V=r6vDe$cjs{S6O+H_FC)X7f6zW3_XHi}s7)XK@(W(VmGXT<3{AYl9aNt~f<u-6|oNGpiG!?;i;~b{6Km>k7hk^+O2PF8v5QtqP!@Fph9TT0Z<dvypJk!Lrr#e9lFDpPH~Nhw!jTgzKKVp#R?{pM?K)mXY1`x6uFMMEcq;4VO}WpSDF`)tX8AqQRii^jvu#%>N-pz!%mWL;K*IKkRQxBwT;^P9)`TQ6lhLmC3${Z8x9p|M3CwTH6w?94K5x_uF5A{t{Qh^_gQ<6Yn(&^>yh8JU3!JJy$Ou`AlsOJCE&SD1T9d(YG;nSa(B<O~gIUq91mc0pA$Cne+=A!G5P2u>YahK>inRBYoq*xRWkk|M(T^?A4w(lq%|yDp?3?G0yLAKS4=Qe*WVB`%h34JN;)rL3MKY|NaD3(?keMm8?{<P^pSam033D>xwE>Qt2C(EAVx7m8z*!gXOAxJwuIayh;<9PgQAzN&zbQsuae28q5BCFO+#0%ft9yF!NBBy;K^mQZ)0QS?;b<h)V7%jb&M4i&R>w(rV`GSZ=6NQ<Z*V-h<_lvfowesgeWZ^8O@VdpYxHmRG8@UZr1|Z)bT5KNG`zIm-swcCrVUA7c5WN=H>HWS+<J5tU@Gonn55<(vG>L*|7npH}IDN>`X)V>w@?TPhVXfBZN3E?-Ojgyokim8kTA`A3#t@Y-d}AF^!VIFguOWceV+B4fJF@<EOvljD=?KH#+_f5h?|m7c0p%s#wlKP3Om@>llB#00#I<v;nJnF+YWq@1G43sj0!=`hO@o1@Y)l@>E!#j@;`wE}&#MWsZQ4lv)xa&whht2B_gH_NjB>;(Ez@*#hd+wryJqgeh{rTQxMXWpA-xz-+DPx3UDWqmJkjU_K&S=RLi*L;9LPs@Im`)9Pk-ilC3uTr?cUY#YdcO{?8vdsG{u7l*IEXzK4C(t87oIjb*y(~*?jKCh)$vlST_8hN_yC2K#Ircs(wc?ojFedMHWL?R7vHTtDe$TuQ%e4gdwlnjeSZ<<HZIwKkyRcl9pXtQhnPsU{gY_iu%Cb2>qha2O<!@A~pi(m?Dc5Cg%Ch8@S+2;oYBJZbEcfbJfqk5+(leFPRl3Tu#IjU+F0hXzzs|DMd#%z5)_u*`36^u1zhyax<t*mUS(bgjL|{)y{)<ZURN5-Ar|&Vp$ntKL?z3<A*;gsc`Rpe!qa~lo@?e2EJ)L<7%Y*pdIOfw?me2a|^O6U$Y{_|dWZsPBdVJ4~xg*Op_+D4$ZY;}r9Val$<r%R?;GB>=mStHlTa_wtoopGCH8tV7N^Zt-b=Gac+?M4!0`uZW<^x%luMpK#>cG4U%W@7h5|{;&JFzU!P!EA~RB|25^1K}?aOO(98{d=Mm1P@VuO;&iEKB<hcn!(hvb<l&-#k%gBiC5U$pSrboB2JK_wzj?^V=*(37mKG+&j;*#1;z7;auj2S(dYPo50+aXX_?`^HuT$mgSk4EpRSM{yWPP1ZGe?^PMcq*)&;TR!P2t<#K^DMV>A4oDh75NN%dqCsnM%_3O<1N0u%4o;~x<ELY=uU6|XmEcerVfjuR;oW*hupJV@J9J@G18S62DnJ;JmWq~;_=e_)x!9}q`U~bF#{hL7F%Kp70aGuI@RrcQx0=?NrpdVykY!*20<hdtf{UQ*roTrTiX07CM_R1M7d&Nqik0h6UBKzeJfips$6&ty(8O(E8j^cagnP;#pYcrecHk<1r>m&DnUxC>mx!n752FP<(&UA0)o-E5;%02Mcd*}?l{%dc@`(b=7<xswsax`B{IhbXMjpXZSUS}lBULGc<)@J|iU(o*hqn8Ex$3LX~&nN%+wc+niE>dm%*Ov${kBV}Zs6)q;0*I6q75@S^O1DJ'

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
