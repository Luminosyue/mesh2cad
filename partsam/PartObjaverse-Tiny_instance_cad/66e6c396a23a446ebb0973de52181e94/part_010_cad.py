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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_010.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_010.stl', 'source_sha256': '8c5256eebec28bf8e3f2554fa5f80d7c539b864d343d4505fa958b9cfb925174', 'input_faces': 302, 'input_vertices': 224, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09749062359333038, -0.3662095367908478, 0.12089984118938446], [0.27717939019203186, -0.24348698556423187, 0.212175190448761]]}
GEOMETRY_BASE85 = 'c$}r02UJz(wuLuHP!T&~P2AW}tib{T;<g)6V(;asfY<;jme{sejb1xyY>DQOM2scTSWrQ9TL7_xHJWmaF`8TwW7HR8Vsg*F=H!L*#(QJD@g8HWF+Zk@^{>Be_F>pJqLhb^hA%%YJU?fdSxwVacxyh|^ytLoiQ}V_TEr#Ha?>h_ufB?PUF4uXeTTVe)3w?DQPD}`6a7PU|FD=~|7N;>OnhQ;;@G$`@rhB<%I`jQN>a4bPl_Fz5bgZFabRGZW_s%;&GfnY|MAPq*@DsV*^!Q_mxYsWo^Xmjr^^}jy|v8!s8VD9c=2ufhr+K_TYRhB1o0hX62&*ur;BgvF;RS@R7LT%6U)SRc)f{ykB;y!o<aRiQQ~VgVo;~(8R|c<p-zXpr^WYm%M@K=h;P09s^r_|$BA$GwMPF{Z%DqLl_0+Hq(ADvb5MNye<WtQ)L+^Mb&S2@YmTOvZ=;uz@3@=?e{&H0q5#R)2YF^mz21Z2?+z8;xau#y6<$YtbB-N#g4@FH)*kEd(QM3X_CVB`*b({Z6LO{g;lbjYdDSuBdtXYv_Hdr~wu%ifuN7W0u03EIe6Ei@uAbDfmEPwvu2FR@>UY_nRdRjoQ{Hj$ZOzJKJ$J=o-4++1&vm`vN7Tl+<L-&C>!mQSX}QRss2!93FSWtA!Tr$xc6ae@zl5OwuyZ-`eVx+CA6&y_{k1)H#n-=Ug*tb7qt6=w;yc<5N1YpE#J4s~7T+Fu?}p5)u#42OElx)Lj_Aksb&QN_S<_M9E68PDdhl%VwTMPopAIi1-^h3m<F@)n>RU^9q0jDzj^TdzBL9`&PDvlTPr(oROY)7v?{Gf1oQJ;|_d-A0Q2IB1x(k0rbL@L39~oD#>y<6ztgVH0sJ=&h$8c})9WR@qj#o46i%%=@^_<HxuI7<1{n+x_A^&sCOW*nt<~w?d_~vt-!+@(;pQmXUH?|_iJv2gmd%*$ZXFikq=A|Y$|3N3SOU~E)cB71I4gN)Z<Mu+V+nKUhhv#m`MJt8j{A4W0I>&p8Z>`Eie&j9OmmmGb*J}L<Kgu2bT-+?aF$CwtF)$Q$TJI3w_WQS3hx_~R{Q2GEg!p4lVP9%{NuT<xMkh-4V>Yv)erkyLMp0X=+qwN%pR8{1CoYmYj-aPF|3y>9H+QwbdAnFe_SgP?viRE7ve@4bqfkG8zWBw@F<Z;=IOj)}y7Xf`zKVODo+`fm)hw*DXFQ%`!#1IQiw@|2X6L+;zT?2nYf`^S+DWO~ZWqQ~TnX#;-~i5>?GVOo(;597{z&SWH;-c7*8Cvj>g!+NyfwXob?DMo>Kk<%NPS~MA^iKi*TLm6uee9(|014~))SlfT9b;F^pg>cdtLNT8CUc46W_5m5dO0E;#)`jk)J&X^Yz%~;u~e_BLBBOxh{TkO^o}87w%nHJMp!Y*Rc+<x5PIOgov;Iu<EMhf0c^7M`7^ee2_oqDDI<oxcKJ!ap>n>SYAor_H^QP$xkmM=fpbE74^nMV|_MVk#Qa8BgMDxb3G4c>3&#;ACa&3iNd_*4MIQBlQ3WR=QvlnV=>>2rE!0k_Z8onh(5=MxSUU`a5DUd$8b(IZj*aqG>f-N-Y@%%3#ij80e<oC@f~NxH-l%P&W1<0U%h|A`$MVq=yT6#^mA-xj*B1nqEOcDS9i>_`TN*kKHrM-%|FvI?)huD*IC=~{0Z3!Kc>F)Z$Dcf&!3;ZMnBiuyFACtwC|AL_#ND%@h#EkCqHA{3m%y7o(jmX`X~0Q@<6Oxm#(-kANtC9w+^PtInkG<%J=rvx}wF;TP=JD*6m;QkpKOUSf95oy#Hhcz>n{W{q;{m{;t-zPhHl@`7yhW!1<}z3FF)!A?s%KdLqv|GbK{|;`bKq?gsSlHBfxBg15`OtVzkJzjP?>h3z5om!_O7c@C|guE0;9j{1JJan3V)VjbG8Mx9Z$WgYB6!N{wM=Z$IBNB+MOa!UHf>vv_ptn4D3w}boebEiAI{N6X49)h2tqo3`Mv0p(aux_#bxQ}mm;Ca$DAN5-YV85caW8BX#xy;Lcpeg3{_#61s$D+@twOo87q=(BrvR)R6Z`<7+{^5r>heLiwKi5CS?*(I<?3YpW4E@iEL_Z;0a!UH<o;2A<$G&`=OJBEBCHK)N{2;faZ@9ao|CJ$Fhj<V1&4iIypR}8(zuOb}3qr9zHNJqKUmErK-fMTXNBz;|@%!*lZ#>Tn5|CHf=Tyo2Tm0T)ovsC+?`h_R_plB<n&3U?&#o@-rFwJ#-bd<>=lgjA_IGYL>g4y}=aIkgJbWz@_t*pPpGMkS7&q)q^u_0=8GaD!P%sdF`y+A=9bewWJ_U_)$v5(!W4`m_us(brc6j^_KYTuX{vNT)jl}!X<Hh1Tik}ZJPU1ec-j4n!50Y`U_i=x;-8)Z}JXf~bxp)ux>jdg=!~49W{P%b-8gK*q$oB_(%?()3Di7d4Z;1QlSqaaV@5^C)zCRS72eV-X`29y<JtsZFxGw`S&Wm^#-}<#1@-wUg>F2>i{Qhp;6FxsjXhj#1-#8BM*S?+L*IkJB0q?DN4|-Nl&a?g9YFLNN47@M@*azc!R^fXT-iwXPy|K>QuA%-kd_Hpw$iTh0)dTZQ3_UOX-_ozhK2D!@4(mS$e(1T&l5a+c@96lp_*#>;m{;ujeChA<Ht`)}QzT!%QUHJQNtb+k%?eV-sCftZr*lyM$Qsmd_l5XI-D=X0wfK(s_6lwnq)w~;QpcJ(Lh9=wVd6WE!?!hd$GF+O#JBnk5MLX15&2KYAm3I8^PTM`<Jnt|L;W^W#5Y$p7T@+wEd0H3(x>fqB-Urx)C(o&Wo{lLzBwaKeB0W;P-j*F{IppZw@E9hqor&^KZy&(H&+iw{|85jZ<adeGB4|Jwu`TCX(PU|auDjL+(rJ{ty14OJ{Rj&bRYe^{7w4NcIIRKUwMJ`@%F?z|9l<mf8Fh({QJVbnAenk825^g_-4n^nAehWI3M2Ckv}sFbyhr=I(k|i_|JMtKlY=&FyHh3;_HPYu@0dZ#CHrg#MdHH(f{K>^jX*ybt<>Vc{}&5<XhqK;yVsw{f*{p;a^QgpI<-6e0$77ouZ}iE3U@4^{XL2ej~<R<mHlYU%AO;UbdKB;%jr#;178heKtx#|1CboyoL-%ouK{L7tf30TPJ@N-~PxQ=cmd|^gq%a``*7i`g!yae%>FFug5JAUwfknby|6&&Z07?AM{Loo0|{TKkMdM$uIK~{_srnbH6e6Wvlxo@q3oRJ_gRmzT}k`-|jaGzTOn;aL8ADN6*u!v*Z`4ZzcP~Z;%Z?Vx816_B9b-8=8pztKE@&V`V7n-;Tw-+q44bYERG=@$XeZooQ$Bxubl7_}05PpZe@>Qb(VVB)*oh9M2hkp0a<qQhdkDjku?4e#7Ur_PdckuRHwM+4vlB`iA&=hauR<9bdu^eS&eXuE2BY^R_as?Sxx_{QLR<oaZnD^%u7kUw3Q}->TIR^Zm8E__hP?=)Y4E`mfegeB+M^sI&bO)bZ;tzLqiq>tA&@_R-gd{M4y9w{bc6+-hGgzI|p5oX?Yf=rer{@}Fc&zIiBF>gzK$iEmCig*wIW1NFBQl-w8F*>LQywg>ZVR~deboml6{Z1|7x{IqxbA-7{+m%rXNevp>)aRp6NQC9QOV#b#E)2%YqSF!&0f4ZI6=7064+t#fD|G$5_z2xlSiZd=U6knzmk}s1BoN<kMlUhhtdX=p7I$7xr^5@hqsCUR;kiTXq{)&2&{1y2&^#=Ji`Ah08vf7)&&d8&lA?J}VP|uPtkk3(b$>+$YsVB)wkCIQ5GZ~6MrJf{zO3q>^K2FUg=W^`hjI(kMp=ZbzIh%Tztn>(3={|BcdA~D0bjAnH*ve46%^7y;PU;8b5BM`XsXNF!SZ^nFA9)|g-bp=7-b2lx9wujyk5NyMkCAhzdE^}OdFlo7d2&AW966tSih7!SihO{YNzUXxDNb|7`_4$GeneKfovic|@+bVcbn2(%bn-6hUh;10XVksqz0CWJnnhN6octO25Y-|dA|Iq?le4)`2N{Y#rtTn{&RFD(B!=So&KT>AXlD#_MrUdVhT>7wX!0oXTxTRwCsCuxlgLrjvE(T77>44J)L~?$1IZ)FL#TboL&$@uy~s-6AP*w<V<?VbDDFn>MeauK%1~@j`;hyv4}+mNggT5|ypAE%Hsla;AVYC;#_P^#;EdYNsNsw%)XL;4WN&IYvNyRjLva~uWpWvE1%_f@Y7Me4`89^(deqwF+U&6&^>uPRaxk?yxjE+;Ozlio+JUTe6gik|qs}GIqOPRQC9fo}p{^h+O(m}(ucK}xuOn}A#=F!l)Q#kKsOza4$?M6hsj1{tj=h?pcqw%*c`11zL-9=Q@4GaUp?Eq&aSC-3S?N@A3V8-Ko;-v67B!jt7I_|ZK6xJbAJj!;rAx^FATM^tGU{^b67t*BIn*WOC9E}vYLb;Ek>`-7Ib$+)3N?wG#QvsGlgU%a6RGj!iR2jSRPt1=V+=Kl977&Q9Ya<+l01$)oS}FqbqIMVc>r|~S!qA=0CIn71i3%CFSQ4`FFDc~J*nNPJ;>e3ofwM4sS)IGau`E#D770ol-!=$mE4{jL^a4k<aX2$veH0uJ92A=;#SmV<W}USRDW_)azm;gxgq&gY8~>c<Z2AXJ`BZ`7>cVh6xX8qk!z9bQvJ#P?5{3EaU+J}0BRsvX>+pD2IK&8W9{$X0gV}ob!ru|POeV%CRZnyr<Nv{Cwoyn$X?`EoZ(J&qk51vYALD*xfI!xTAJ)hE=w&#R$75vmRymcxF*$?T$5a%`Wm@DxdpWexdpi`Lvc&$Yh<PM$V!9B>a*TpXLO;CCU+tCrj94~CXb-Tkw=hYsk6x&sGF&?$(zaVF%++5C|*U4Bgb*PRSd=dWGG%h9Zg<9PM{7ZCy*yF6u;?=z7cNjKBfMr|DyEwmnjFM<bPQDuRrPf@wntq9(UII&kxIeBVJMG#d-ML<pH0jPQUhVgv^*a'

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
