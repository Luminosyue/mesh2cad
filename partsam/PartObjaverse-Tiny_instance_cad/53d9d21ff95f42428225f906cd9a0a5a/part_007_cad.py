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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/53d9d21ff95f42428225f906cd9a0a5a/part_007.stl', 'relative_path': '53d9d21ff95f42428225f906cd9a0a5a/part_007.stl', 'source_sha256': 'e67b3a8e8854721b7e2854dc0e48c965bc97bfd0d593cd4e2da753618dcc32a5', 'input_faces': 266, 'input_vertices': 294, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16525405645370483, 0.10614168643951416, -0.24535603821277618], [0.1707242876291275, 0.4806796908378601, 0.0768452063202858]]}
GEOMETRY_BASE85 = 'c$}r033N^8yT*57CZ-^UB<$1>)lh0^gzBb-HX$f#=7<;)B1rz`>NZ40P(chy=`jW&h8Po)ZHg%oV@$zOV{0l+)zI?a`+45pD|g+y)?N2zt#>_-U*0_5xA)oOcXSCTRJfwTA1|fk?nM>Kc_@liE=omZ+>o)6A%llRG#E8{qLWe%-1_-P7X|j{)TOtRGESN79Xupr@K|p@)w|_TUvD4PduaIB$gzV)4GbR}JjCMd2aSvvV)BULgGLWA|6TW!=1qLm#vl5q->Uz|pOWSj^itkOGc0|1`@-j@I;LGdVg1`NvKF|qKZ87})yem{-l6bCi>seTpkFPkf@>@PM87)qCb-h2I{Qa212-ZQPZr>-&w^_k+MQ&dCv#?dAz#TV!<<+T_P4A`USTr0*0>7ixoiV+^w=%Pu`jMfo)`wMc$Po)KG(87MUL(J%E-}smSg{SQ_yeg<96zOuJvw(e*3%4$I<s=F>vEi56&lT7kQh%j-Wra54dr*6M5ouaKj~%Ia_*wJ3=0lUvGnP?e6n9ZrDBY7UR&b&v<$aIlo_Hey3Q@f8d|s`h>IWPoB?lD=s9jo(Zl$O=8Y(%fTIY_ObuYD$c)_FY{xP*?-3XcWAB1S9Std-h7shc|Hg~gue8S<lS7s9l71X9X0&P7u7g`<H6WpkiTsQt~I_`kXI;@ft<}x4i?~(KLJ<!yP)3|+?qVM_I}Jiy7u7${K%K!djA&Sj-sED_sB<%<`r}BeXg%?HNZzFfg9!Pl5ZLdZp3*P;L7#6;I<k5;7WoUc{QIj%x8lg;~Fc=GAFIXLFDH@HgLXVlp){v1UZgj$H5)h&+&K4r5N<9w-<xko;)Kj8V+tO4FlH)oCnu~o`Nfh6$)_WdFeyQiT#ZEqqnhtS}3>{7LieapP2)0o0<h~ON?U94&^ZTRZsRGn@N83I{F<k8R_`<%+AdDW(@lyBEfBI1KEEn09;LUW&gTz<Q})c?VU~>z`yU6A%C_PTxlBwuAfNY{?0gf8RMR<#Lst+PCl-|74(<RpN{jS>QwTQ-r(Argz@-X3Wbv2W4|%$Jh(k-D7dD%GsiP+IQW9D?4Mf`Tt5~R!u=b_{ynAHUpK`M^ZCpdT>sgP{W~vd;2BNWfAcNouN2O(VSj|Vv%hx<_Wzka5L&h}`#tWWUu)VM$G_6hjePiH=GfPdL4P%8=FENsu5J!RzrEFKeE!;@m(00e4gC(UeDc*-!Hpt8laSZ-61Z{g9=P5)cOpKY+${Fz9Rs&z1y94@wNK`8_s0cr`^$3R_WG-s6Sa%uCXI^1ywax`{Cr<?o==mxf8Tw_{xXL-?xkwzSMH5vzp<J;HZ&SqFO>aR&e(5`T8EHhd)b+M>2_|{0XO#dZ%<zJ2j;{zn1^|tRhb{OlKscC=3@K)sKWk>6FC1-ehV<)?zeFsC}Gju-Wlb<mAG5vay-~h6ykN`X)?Is%;P~zuL7?69L9N|{ouj=HN80A=u~h+X>tkMwZtnE`}eCDo;UUCaC^s(;(2{#1p5z-M8A6fDDF>=9W9w(D-_&*JB#-%|FYnE|2XDX3kJ8{yUO#g^FsE&7{Q$8yTP^IY3v{6#QSCI4eXESe3bMa-2P=#*ne#g`n7r`c^~x}0dA~q$o+74Ci?9meVNnY2IpVvN8X>ls!rbfD(ACuJ-EG>GjrPi4X(6k!t3dqjQtqrmzU&mpM%?GCxR=!Rrz_HKhFEbg$3Yxo%*~E`2LPub;}@dBeWtv_tF>9uZ<5Rw||O$^+s*(_rJd2xUWCq@iVs{^Y6S&!|#0>aNKnvyk70PL>?Bv{#j3Oo@zCs!F8h@`GCK{)y<>9m8RTp_OS~wo?~kWxE344dD^D&`f#=$`+sP`d0xsyznWKx`H}tD@4JBc>z&#EVmx`D3e1Vyn2P)>V>qAkHF>{Ywi?_RDaU{0THa6F2c*6~PklsVj_2PNTwfo@>vm3Ko~JQwnD3a*{8GDkT?>D^5BYCp{%3}9J16}DuDAY)<7TJx_)m9`NAtYa>a^$e#3u$^nU~1(J**w?r;Wd5ey!!4PtCKuFAx5J{jZXFU3Fi^``v@e<c?LB-#<?^kKKDQZe|K|`mE!5wQeoA5wMZlWe$t{phn<YH1qA5r+9zt)^Q8+SI1q$Joipb!T2TaZ$^K9Hn_GeVF!MnI-9(G?L73|j7!GvTSk%pSs2__KY2Um6&M7rhsPtwu5L!YcA+QvlW_E_dx~#H|KmF3U+x2UtQfcvd4E(PpVNZ*J_okp_kWcHH@cqVJbNF*Jk_!flF+}(`8xK)%-!qJzbOUW=w5>3_R8J<KG&Z%0yh%hV!PA>3&6G0qscEMY<-{Wdnbe2XM}S8t>&@cJpkh>!z-@Ee7lAwaX%m7xQ`BCyYzlNm^0yX@@2QVU5}bF$D=gopIbT+IqzJ_b7R5v4ii`5_lq8F!gfWhVNQ;*1^r9!g6q4xqu;S_1m@#dd5OGZB>J@mcd=cLjykwD{o-}*&%_nbbN^z0Y&`jj6BySX)|&j;dgg2@iv4CE<Hwvy=ed8rzL11@Re81%^US`^?JCxKCA7{(aD7{)8<=<VPnMxSb2+$HHJAH;s~h&S-Y0^*<~#B`r?5YjurAE;@I;RG=m>Hg^U8xO+q!`(KJg2|6CE3n^R*M^V?SJS6ErIx+^Aod+pFy0{tsNr{+4}^<G59O5#~9yCAeZ+0Im<;#{0gj8@S%D9*>7XkCCJAI-iJqmnG;oZYRw_ew#G%37t8g4d1Q9@AbCiiCsCLm_6W*=9kxlM;>NQwR(7ta=Zuz*I$Qn+;3m4h8_=IjCo$1#^YpWb-ah#JBBPm&QzX{_Plj`&mGtvT<N%opKqONeDBWdwGh8|)0xw14f_N2Sd2S;IIj<t8u0zS`igy+->1Q6kRM-q56{DG<caOT9pf(TM$Y1Tso+iOv%kj-T))(ge&Bk3S#b4PAh@mkCi1nv<{+o?Ltbb7cY`a3c7WScc7xk0)ZqJ4R5-Zi-j(;E9B*)4Z2@lV_8_0piv3^a@cLOj7S~lRA)5W09-hYUSES;8XJ5L2{WJE1>%Oyi{|-n5*LLn<&WBTYeU3^YkK%KzvB{tJmthZ?-!&LH_P!tTxhnWM`37H(E6)!`*Ghc<9CU#9qlOxC?BCY~*9u+c{b)Gf`?TK!+27}CHgc{n<a1HO?tH&(xC7jnFo5?Xw<zXxK3L#BsGLdwHx^yuxWn4=IkVMH=G^Vb{O1#Rzni>|<NDSGcVrCU_V$0qetFMQv;3Gd*A?&W%J{Rq54JnV=i8#5;QF()EQ~wRi}&9smHmg~!Sy=Dne%fHxG`-%_rs<=yzlpz%zk?v^c$;>vj6;4=9eoDZvS`-pEq1$$meEqd#APG^GQfHb0VToA!mLtpK~6ZA#WW{ezg;M?Oe|1-VT25MSc1FbJ_{(8b-uE^1hi|e^5NY_2TzWLh}?p?`3#`EC0$NzyFZ^8#{n&o_r3`Zl&?P?AjpaOlyUHwcZM@8^jN0&d7S?`O)C&(ops%PC0@7@Tw`EZylwlu)kCi^PBlICuu)<;dt`AR($>}{*LqMmO!3zg7XjY!}^Gk5W~;CcRJt0Gv;J)JNdk)oombI^Hqnqo>F)+`zJK#d|tV5-DG^EJU3?WxxHf@uCqKH%HwD0POh5-`GG6`6S=PCx{vFAi@SsC?fS64YjeK8%nf4y(O|B3)mp;q;g=(r?-I!VKkK94?md!x$roJLD&o&|$eppww>9KC*h_D4HG3uby5j85yHJqVZYk>z+xZ@JD22R5BOcE^6ZyWAp2~4g&SSr<|LCa)Isc3oTo*mP1NmA?4*C7#T+ht!&-K8V8_e0Rb3gxelR0;P;eLKmjr^Gp-V;^l-#DMnd%6CZ*%CQgzc<Y9SDyXf)XaRJ>#s)h^SyYJ&*xX)vcK9au8X?dM~<50&h@M=!Tfyl&hq>X_2l|g>+$SAkjZsdrv~H;@A19t(N>JB+!8M9pITH{7LK34n{Yj=MHgP*UgYpRI_D3rcW=sd=}Lj<H|BL?j-xH-bN!H<*TI};qj%?_2cMu{T{Db1ji=yxVteyq4dyw0IQ!>+#2nuYo=2@iIUi#cuRq4nwaDo?mE(T@ocWE;Fh6o8`zv~J{xx=RT`YPT#~oaV`#)g|kN^8Wa@=*P$T5_VZ1BA8>_7gB`>pkAuK)Jg#r}Y;=vNwcWWVcC^7zYq@9t~oy7{(aoX>_Tn7<=&_Bzb7^GW8%wcz#kNj~|;i`=eB5y-dKypDYPx;*k5IebrdibKAt-e-Q=a=xceS-|6}|08lo2yz_d4<SbzQ3mUV%DKAWs=xnf<m(@hS610yxgofc?oB>*2d>-7z#@1KQ(AsRo_&tjbMH~$w)!2&-LIVk@3tK|#*E(NThD`Q#&U4|>385pk2&DBm2Nrce>jW%yS_rc-7AdGm!VuIRb~wZcRW4~t|tCKeqsi4)RPKwY*#jNy*0Wnxc&SvaAp53a6RWLuJhW%Og<m`-DS?LKfvwHYvVcI7Tyf&p?dZZ-e2}s<$KHH=H#|-$xDvmd(O<+<fnhZ{lZZ!gztyWbIA|C<$dJlF228AxlBGb1YGO67w@Hxo_XZQCzEe;N=AO)3P&){yu9PkNqx71r(6ct1AKCk-|Hh@heIELYpZL3E34dje0Fy|ihuu9jQz4srFK%m^&xL~UnrH%>+Qbw;9BEbygttl<MrfRH}bD?!L=m=!5wNOxUp<6zqj%$!|zA>=p1)`GQS^bt?>JfQY*<n=l3c4-DL718_6q1k!P&}*S<MQUMGnB<FE1kj{590=i|@sgOnHT$OEo&K3~)$kIz4z(WSt*iFdwe`ue4dc}Fs<gi=u%I_SNx5-n)`{G<Q<SBW7_{&!y`Hf#3({VLJT+9hUHlCpdSQCIO5#Fv+{d>PTQ;w>#LzKnPm(URg_#1|DUCcdb6XVF69oyGt2V|gdhBI3&_)=oA*cG1G(ONlQo>LlJt{?_vM&3bIs9VyE{l(PIY(ci^e`bzvW@h_w-|624f@vp_d6?Jx^x3rM>>t;F3x+Z1$o1%Bc-xPmK^cV5B#NQKrBL1HEN21TgKNA0&=u7dxiO(1PTYSFwH=>1|=--HUa-tR$?<Bs6Xi4!!#FsFutXZYZDkEA#d<p5X{8}@Am07E$EdP_}kK%t4pCGzSyrql9Cx~AvW%)&-^Tk{Gz4%4q7f4w?Ms&LP81Ye}Q^i|4MSPU_8B&)2PIR*Pu4Z*JtGkrtzY*;r{u}YVMSF_3w6FNy;`>Qiet>9y@s<u0KS2B-Da!|o4i+CQeyHdW@s<u3KU93El;ua7HOZ`rW=)W?{5UDgM~aRYZ|T3pM~WXSW%+Q?2=U?K!$e1mA1&jDNm+h`=y364%nC7Ul$7O%i3W)uCf+96N4!mZFVU~X_Y&Vl%JPAtoyA-FrT9Sc?acbbtd?fA5^X2Go%C2f$*e7AZIZJ5X3?$UH;Yde-7Y>^{5H{@;<t%U5#1|3Mf@Jo{o?nCPZKr7r-{!HJt96s{9(~!;tz|@6g??EQ~U|h)8bEv&o=9vS!c{TE1E4nTY4;C&AfJam{nEE^6pZW_Y|!z-cnV(r}!FDmiH3<K)jdunxeJDTUuNEE^{9H6zgkumgRSg9uU7<e5zSb&3a(gucAMT|5f~L(LC|D#orLUBL0T>tD=|0Ulo5@^rHC7;&VmMi_aB*K{QMJ1@Sqe$HnJ}KP7rd{3-EAMbpI}6@O4PReY-K6U(nLYo%FsDa)@AjTgT{{BqGH;w_C8zg&Erl;szS&J%BGwD^VMe~_~LT+x~0=Zc>rI!(N#y7)QbXG>Xrmgu+Q8=2M6tdB(-i2qo8eNi9rmVP9@zW91lmai-Np?FK{h_5T&TgvjaMQe$#E#6D?1M!xs;=RPzkg~kHsE2q<D~op*Uq#CDRYj|buPWYCw7PgpYl`n=R)AR@r7Z6+W%&-GUx~N0z4#8|+e%r!jp!HR+lbdhTZ^~!bMcz^&!jBxC)z^1rOn0riT9PVd^6Ec#Wxe*M6{`ROB;)?VqQ}!o8=~2NxYl*ilP<7R}}9mT3)=X_;RA9#g`NBV%8t#c<;>mQ_Awz1GA;Yoan8xd~s11@h*~M`9!mAgIVjOEWciKqxdcXPR<nz{ZIb|^FM!dYs>=wA@jffWx?02_y01`%=(X)uPy;atoID_rNS8x0@JKBMEN&6kj}j'

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
