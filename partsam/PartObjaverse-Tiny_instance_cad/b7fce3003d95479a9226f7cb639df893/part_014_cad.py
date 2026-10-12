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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_014.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_014.stl', 'source_sha256': '66c21a536aa2909b6344f3b29909d548b11d672a4fe1c9360570ddb3b96b8eb6', 'input_faces': 380, 'input_vertices': 277, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3995800316333771, -0.49889716506004333, -0.27146169543266296], [0.25984954833984375, 0.28813183307647705, 0.46073558926582336]]}
GEOMETRY_BASE85 = 'c$}r02Xsx@9>!0Q5G7jlcC<u$x=|)37g0u(j51`*aFJ-ECVD;kDA9rpQ4S%3hru9*BqyZ1kpu~ecE>1Flo<>L&%Cqu{`R%cao<{Ry%+0S-|v3e_rL2o_aqVEU$}^;#J*}vzim$|m|0blh)PPH()8evsbfb5hc=x!d6tV*hUVmpdw8FLy#oSWr0LQe@1Wq&ks;n4WN)8Q?Yx`F-lHakObr=6aoD7gpkR`B8$LcXSkFVp44)jVzi!a7ZQCYttA<VFdGi1GRa_r}9J?VufsDnwWQH$sTcMK)PI9^3vv6m*egDpbzD{y=-OV^!kLO-2w<5Q8YhuWyO<oCxoY%?rKSf?!S1!0F=8FH0FlV{s(>aE?rQ<JGNv?!_nk3H4ob!2^b3QL~&gbRGJ7s1$t&jYJ`p7@1kDS++kxS^;YR=K#kq4b*dC}KN;=1u%NvobE<`Qr3#@h4scjT$8y<=aZhp{@lyiyG7Z_4@l^ISUgN2as(Ja@E@ot;bbm@%yWq5i89oaB<Vd^BCRBmOj3=B%f6<YDp06P)By*9KeZ>z3VE?xWCLE!O$4uan#|WXW0Tw`%1&o3A-{oHyj=`I>XyUX|0YINL9toA*oM?M?gT$j$rJee)G(=ZEL!>%yG#b8F7|xi#mislNGqI@+7A7jynWzozTOoICC_M|-n;U6FM0{Frloeyoq`v2mWilOdiTbI#9?_N)r4GvIE9cz(>e<NUn-`!cO#x?h=dejb#VNi4r=i=pFKe<hL5dwxGddww1?o}2EUN=J$1b58H3<LcL3qq*(jC9yr<7e{Wo|C@8ZFXo)@i#g}}qGX3(66a-Uz9pIV<F%6J%C)>?!+x1^zF*4H*E!<6EMsEWx$|Dl^5Ijn#C<g9d><{5BUt`(*?6&EbMCm$<oK~X{cV=G@8+EEyLE5}!#L%~Nk7o<S7=Ie%d1J340TL7ucK9~OLIk=d`X;_Ip_0|k5$eQ*IBzfh@N+O^nz@0JoeSWX|(>ZHm1CQo;Nx8*Nb8ub;O+uwEd!~nTB(9G=lDr)}b-W=a0WY`~B@H+qdKzhV~Y1G_9kId14dWs|62fZhw<&WA6`3r{}*xo{hGj6`pPw=iM!I{FaFE>0%xGl1g;G>Q*g{=1rGn&^lH2u=~NCW{I@^wj(KY{5kdL{6EMi4~Tb`t5IhYoz>BvFU_I*K4)>9nA_E1bU)0w<f_qqQ@;P@3|$xRxfc!NG3C5I&!ze)an9QFT$|M+-dV0xt)1wsj-&p7*|D_W8A&#A{N~&-e&kA*Et<3TJm>Az7RTv%Qp)vb&vP!F>3A%@yVyC4xSlP}%bfFZ@?2TbGfV8(ob!GixwYY0r|prO+e;M!PB|M7&!zff;+*Atoc0RQ(e!oI;_UN(Z6LiaEDtP(Tn+b4rPoVzwLP?5caJ>!{eS&r$hBOzD`KuJ85~9XkBFe{<%OT8h`Dv?yvt&)`X_Iv^GTgW+goQ(Nf&c@VB}>nSKcLUruD0SOrO`}@DpibE?3LHB<8Yz|8Q~q^2>J_V$R3Ub7g(mHR3vG&Gyp!fD|xjF>QA%gSJ<L1899IXXG4lzFKI-3u4aa>&V~k89`r1wWsaX0cq@cZQYAb&d#|x=jVav=5ub&9qrYhn;P~vqAb0SNyU67(EV>QgpN~rbCB(0MBH-fmfiF`S#uP2okk2<N!y$652oC4{UZP1{$R>2pLCCNmRkd-CpxRc>q~K|VZOq=WLJDnt{u3+S6t`(Ncy>~JlGgcbJP9MoICC(@8)mv74}z}=BkM~-(Q|f-qvr$^;G*TWS={;?rsyuDP>h=&qYm6?erDTRmZ>1(|lfp>MNXEEeFp_$Q{=m&zGFo?JHat((<5lV$QD%o?F}&M~U-w+)qrocI@z3XSrG}HPKlezAxIm?7g&qeqHy8PZV><b&Xs}K6XG{XLWRPl9=;#=D9TA{h+u$%9h^e#hkAX&n*c}4~grq6@JR{fzn~a`B|m0`{Cus?B}prZP>o|p3BZ#<K9Q9-;1K_Z1s!HCa>+SY{zJwz!dhJ{&yqVUd{DAPTTvPW4{lmU*$4wch1K0n}^x`=XhtDE2n0h6zi*{{OEI>^5yGOVtpmillH6C%swrSQx4g6k-m<)!JgL&p3{D{v_ErczHTgi{?$T%q;)KVYUR=SR(`^MUTN&co|8umV(aiEl>PiYJCNR|>_M(cVy@gcmMP}aP$fZ}uYKb(I!<M;n<mcJQv4{*)pcv>{!39;==-()d72?V-Zo3j74Hm|`$e+n^P24EPDeiOVWybNZHm(KE*&UJ=cR?0VxM1@8Z6)IPT!~Y2u(8N)duH?xr|&xt|3>|batJ+`hwlZH=jusbLorkGYxsnsPp1_s*655Bj$WPd2Wp!dtMyBz1~auKI^h@LoQePf!3F&pJe&iLA0Hv@!cdbSGqON6mtvD(cWs#yR-H@*CL;>Jboj)kGxo9$Snn7*<x--E+w$`R#UE_J<rt!9&A4+o?@Rvr|%hZDJak;=E}a(%suY2`AXN44SCmwnPM(`HcS%Fxn=pGSUR3fYm&t4MV5o;^{B?GtWNDb_Wi<Z&WXA7U56|&S4!q48LqFxVeESE_7VFWXmpOPbK>1|Vy?vW$u#8N?UD`Wv-|aUL(b19a;X8!9p@9d)v_vCyk6wU%s4}i>xJj)G?nEgx3Y1St8?Cvcb|4q%(W>kQpEEhXWY@moSz4t+mZA0U@_(VJUH?`Ls<K-mtQCAsoYz5o%R<rG{taEdb0LBcbpUCcGn3h;&mZ!T4>1mb-{DV4LQG#%sH+Lo?H4&XF0zQ+>47BbH{xEx#pIiB3{4R!&0=4wM&as@jOe><BU1ZGtbqycBx_=%Y*9lzOVRQHRM{M2=;r0gKudrZ=Q66tfyA-;~O+D(Uv}6TVvgCkzAd>kLK31OVSPNKf{l%zf@CZ&&!d|=<mgqZ7R(z@?iFRoX3xDlicq0kk+vrJ)I%;Ydv{})hXWVg4kX@I`<~co5frZ$D<5x#_H?|vl;5UtfRS9d#_Ebuk`(q=34*Rnd11Z<+kS2Iy=KN#roQ{fwW)c%>7KmcwT=+b8T^@i-tOPI$aZU$2!z}N$X2P>RdFe^Y6V1Xuq9rT@?G3JLS<_+u@!i){$+qS^YLXSz;a4+B~0~%aAN_oXViVZ2enb&l2lfF5jf>?Y5%XVjcU65Zd0_pi;JBJzLMB<B@lMWoWNF_GIJF56U)-zu*nK9<^XY9j&hy+piky4Y{1)&i389%TUMi=y-u|fZ?xJQ6nRo29(o(^3vrlc}k;(3xBdAA^GC&{7+V6TmM&ovTD_?`TzSTt3a~ly1s-64~2gL9t!>nJ{UYuS9e{5-~+&4!UN$0z=7b;A;SG3!hZ1XU_bE35aCbY1Hqqw`{<gaYo@Ms@Xg?L;7t(WX!t%b@eSZ;@LpZhb<H6A1m6e_2k(LJ1@8f`hi?EAp8{SFo(vxao(v8~U!?Cb@X_EgU@LqWco^Pig$NIaj{*}P0iKEV8V4T>9*ggfgO31D)D@&_8hkvMcqo|oDlqY_VB%rmY2eLJ7}h=v?e;-iv1VIQYXh_jYqkpgO@Tr&zfg>66f_=l7>{v}fPyfuAk1x?FwdFrY2axXE8z*crs^6A5&jw?90Czu2@&1`Uk%;@=4WX&_IWkhO^2pppQobl(a;3!`2>t(7&H=lJ`!UJh6qoFhe+?w8{zfvmD2n3Nq7%@3wR60O1QDEP7=A@F%fPL5v~hw4kqpat_!Y$_f|r^#^B=cqTu3S7kCwL71SYIM^^`3O(4RZ!6oqhI^fFiLg32aV(`-7V&JOq7T~JjdhpKR&ghqLBZ)k_zn_-{>p{F3xD&WJycD=O*aPn^j(Uy2?r;~dJ6M8yfIU!0!a9)g{R1N01>OSO1>6#CN($>)5^F}hFt`M`5WEby5V$nFCAcN(6DIrKUf7rRSUci%!5zT$(5ABV{=5;c1TO}z1TG4%3N8w+0<Q<Ihx&xc$G4X*H;8a~h;V&~un**geQO3T1@{D(0!wf=>HU`*_RS4_@O>oQ2wq=$zwd-Ca38P_`X*dmS2bP!@SfmSx?1b%3hxH)iFRG#t%Nq!(XKjb5bmezGhH>|HNZV|eX6Ss{3CE1wCMr=4BQXz`xO2WI6zllT{65DxR<Wpy4u3qf!m@@FL+;Y0N&Rd-VWSRR|8$%5a9|CVONN7MTl@yh_ElbBiI+*5bh0b2rdh+04@tI0(S)$0hfbU1Xo1ggn!j_Mb{tjZ15l8-{Dzc;=h0|gR@ZQ4r&lj0spA$XI*#UPr!G<Kfxb^?eGWi$KdO_QgtOjgwMdwgU^6}fC!(3r-9FcHTVs%2F`##180Eq;V;2t4Cxrxb?{SoJ~$uk3BS<w3N@aAU&8+czXU%;P2%_9e}eCUZ$X3~!e4<Of}g`*fS-dO!S90~fp5dFfp3HJ;1|GoU>p1@*aptU*m5!6T;zQGSA})EiaorFTB*<l?ArzOeIB}oeY=LSra||yZ}%~`8}Mh~N0<*^hugwh-4@pKHpZI^w!!nj$-2(zx&#rv2ocVNCxSD<Iq)Q~9Zp_95VE<t6kUrT!r#D`fWHB+fiDHG0WXIy1}_IMgf9Ru1kZ!d0nY=^g3kue0?&uf1<%D;=VLqy`d<oO3@PYm0eB9ipq_$Sgiq)?s_R>b@Cx{M;1%Fy@MGX*;I;6R;I-iGsJRpUoB*GKZwGHjd&2v5?a~zm5#9#h0p13VfUDpLa3nki90}eH|0j4i_yGJc_yG6_{1EsE_#k{gct6I<^TWsvqwaoq3^)ek+YjFX-hp`%j@5NsR{=Z@TmZfaj|blbpN4-AJ`IkA9|w~M&3C%FyD$+hrh8!*=5O$t<b;2N{{?>s{tNsXPU^nKYr_AMm<YSLFn0&LfJ;JzOGAW9!Ha=QflIi&A8QGSup8c69`%Tq6Y7^kpJY75|CX2tyW)H0z-4uL=qdscE(8&ND=`r+s;fA>4BP`;2J8th3-$z;hsvVw0DqT4o`wI@f1!T=rO+Q3#Q#ujey8!*SmHZR>a`rd)C%x-rO&m6^nc_B@lNC?2kGBIPpYv'

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
