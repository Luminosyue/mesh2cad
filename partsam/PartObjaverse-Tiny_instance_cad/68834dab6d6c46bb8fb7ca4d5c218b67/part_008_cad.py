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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/68834dab6d6c46bb8fb7ca4d5c218b67/part_008.stl', 'relative_path': '68834dab6d6c46bb8fb7ca4d5c218b67/part_008.stl', 'source_sha256': '6d265997e8ab2b4117cd4e6d62a2da2976905ddf11c20df41bde106374c0bebf', 'input_faces': 360, 'input_vertices': 228, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3672472834587097, -0.45629191398620605, -0.379386842250824], [2.3558735847473145e-05, 0.2344847321510315, 0.4587986469268799]]}
GEOMETRY_BASE85 = 'c$}r02T)X57KR^!I--s_j-kyu#xbCdp&v>VQA9y;KpP206ft1l#)ts}nA0?7$Akn0B|JdKoEa4bX%PoWDk289*4@76{BDCaTeY=I)vf>QzfYfc-i@!jaB?s;t1t0iD{0*BsMGoek|bIUslGJdCt&VWFP}NxX8JEQk!q7K{=RD12p2~uHxp^Tw77$}&m6CS4nM0p4D{{Sp^K`6@2r5i0iH7_&I<7M5x$M*j5$6Af6f$7e;>o^jy-$!>!Rw_sf%i<>VNz*H<X~1X&)ttTK2a%uQrJ6vgC+(tts<of9LWTHN7uSRhRd7e<5EURTeE?tIEc+e=IbP;$7xa9{p!~_7D2TQoQr9820Vh4}U_}m6qz~tI4-wKiJ}|c&)g`A0quMvma_6O?jqPxk%Uj+?f4MHc^yEV|7$ber@*m%sfZ&)5cT0^6AS%^4EQ#{L<pkB=K7Jsf7LeCl65k2+pVZl+Avb`>FExC4KsX{kQSIk?-(!HT!AsFOjcz*d0ap`|$?*VS}lDmAbRS{uSguMENx~|4gPjKPI#PEbTDmcWp@ht^Ifkbv8Rlbvng{vVW5O#{;RqWS^!NXdFKtV*lNS6XokyecZu*zS(j5{IFqBf8|TA{%hF}V?R6N2;JB4Q>pa&<0kf3r9_Z#cQl3l_3Z1<dkNKg->31{eVEPu&6D9YuJ(4D>G~i1+4pzbMgBqy8W-({S?mYb4WazwtPXR$AN#kxX}lEg>^Q3PgDd-mg?wL5A(!a&2WR$GTSn1+`F*)S`ATispOU_v`pxwpmuXx|t=QN03?_fbXBsbEX<zoe`%}C&aC;)vS=xvF1@AcCc`uERrnEKt?x#0W-uXEv>HX5C>`MuKD6jP+8h2G`1NP-D6R5slre9&d4*MAojtP~gAE5fB(pv0m0+v%h$lG{cy|01#o9v@H-5&i;b-sW12l+i_uAscOol@8@VBezeW~#?8hvu*5eJ=Y_tS{vq>PdA<@9(j%Jw)qPr3t*s{$2K;jHWtubMxcrK1yz}Kd$O7x~`ocT~}Xnll}BI6t7<rf12h=Ni_R*8`qFpM{)m@>|p;(Pz1$$7G162r<WY1{+V}@`dL-7js516V#%NKFpmAL?E7BXOP{y-O!;;17Lc#4(Sr6hdF}?vqkA`><7@oM>)ByC&;NI$IKH_r=bzn>?pO8BiQ_;2{S4*zHNDR9j_l70OD(@1^~Daz|BUi0_UYU|#WtM3`V;nNtfX<#758R;#+wuxch{NcsQ%(!>`z;m!s~ZI7>$4NkDR}oZ#>oGH=M_}xIM?W{gubn`*&KWs^U5vAMx8ony+J5^Eps#&i>?0$rb8<YsP-(MA~Qdle!$EI^VueBj2Yo#Vey)(EhJ|Tf)BAT7~M<)~5BXd7DqZcJdyMpEsD+m*#C2`EuLiJP-UTQC+IHkJ;~(NByNto=W|!dV8CErQJVxKON~s`+)9EEMM0<i>@mT$>eqYCWifpMU+<w$~i;zzlmT!AwQAgXIDv}dfpu3I@`UZ{2Ir5sqE`GzOM(ZH)VVc+Arld`?*fb=QLjx_dn@elHP3LIy*-3zByyX4bnFuoCo`=WZ8=9)xTcLe%yrws#86Z>wmp~^IJ5h>uQ{HX#df^p33n#(MQXVm*%x6$6FU%<N4Bot}DORaD2uL+Gq7PGb8`Xm-}|4eM0rxnf)OxDUZgdF0C(p(J=PUccVHrV?t<Om0sJkA3TlDU!9-DMUJ;+e`Or+SMHlvRPclQ|4P@LFof2brl>XhM|#rrWT&N<*l)?cCY1I=IcUm$b$LHHay|9Kyt;`M;@z*&I#GsqrFAJ6HRtiQin_+@)$%6YZ&5?;H~SJ^&tn4lzKUvbyu&8$M_Y9Y$JgZXb!<eRmjYKOa(s2p<CILkJih07S~rDNIezr6TNF3F{z>*LbDhep3G{k!6B>7=(2V`F+wXEck@S4=Z{Pjw9hx6jD|O|4d2HZqs@F0&l=GYLb=?|KyyUi-`cGR}^nhOX4&?E+JVV$0*4K}}$>(xm9{Gyxdg>qTsB|8e!W@p@UB>%}PXhI;s_+l;wQkkvy82~}X}na0X`JVbBi)xgvpM&F;RDX&lE?jH)iI2;@a_Y?uQhaE(umqxx=!IOj=$)jqw5SYq4laSNM(OxC3?=&dz8>Qs}v~gJ6+pCpSSMH`%u9J_RsF+e)h<x^{Xq0<@%!r-lNaEytvGHVmSW63SMtREtCJsm%Z!LKB+A@&VEcd<<SnSNBfDYU^n-}xmx$>eRXr{f2m+S$0sfhr}&Xse4Z4n;rQ4vikCgj>A6VBU&?h>_Khq*j^FxU$5EH>&;5C^FXtO%PUr1cU&`;o&sUS(uCwn)zCL0LkJp^BG(Ot==^S4+ke+X~{^2~|^W9K?2J7TkdpNHH*VFPLt@E$z^jrVyy4L5}a(ziISRa3LqB`=dIj?`-PFl}_p10Xoldp<7O#Ljo{*%WmuRr;k<O{q$JQi%Ddh>dcuRCW-{i!%irg72bb?5w3s_mfses^fyYx3H$e{H}as@LA0&S6bn8?L|CJ32oUO+Md8UMueB*Z|J2c2n4I%J+3?H=V0G`}UDEzIin`&xKDEubt#f<16Kva~{<`e*VM0{jL9X-`2k};XJLo^SO_6L3vfidFvjbb6PWE2hA(ps}Jn&G`&rAICM_s`1d?76T<nv2iK)}BEQNYUzdda-rH^u`wux!o7sF_Yd+7VS2x&C{+;8sW^L&@udZ|c?Gta&csN(%=kweIp5Lk6`T50b9F2pL8_)622mD5HiIr$RD!FkS-`RuemKVA5_lw*U<g2c9q32~~RBPHlwYkSRPtFO-Bh3w=`K-x3!g+qm;_nq6pJ<+Fa>Kd)pYq7p`nuBhFIDai&eO!1_IKI#4(%tZTwb3_9}_ySrLBq=`&%mbiX%UVs&dzJo_^sRKjP{(y1zeHR`3<i=;Nd>`*EG^f8ghe;aNNnU$*3UTOWQ-vXA3)>ScYtZfopQ)-F`1E~f<hS}opJ10&W_|K#NH`e`$k_tWG=UiUfaynnUvBVS&aOP^D{*ui-$>+pGM-<j&sWzS<@PNwG~&5$5^&XKd7$d}Y!S9zQp(QEzlp`2g6f}f+7mh!owH(`IgBfZvMKFN8rBB?Ib*@Il4l?mOKCJV2}52AS0<&6}t$@-OiZNwb@+%k(K8kejcJdaLSA=N1Xq?%_FIZsq~u2-{^zmGh#V?X9N*X3ND=B+NX2m9wcbAJ!@;C{-i$JdR!%)WOSuj|Z8IByF0Tuw6Q&&Or)xgH<P`$Ry_De`0Ya9mU~?k}8ca_kQ7mn1tr=ld_9eL#xcLcTKY1@DiS6|VREEbiCnt=x}J`z~?ao*bY2i1TcS*hK5}yd}q<YryM%NKKwc=X!B`stbQVaPLje!_qlE@8!7De7{}?_?(LQOm)cidHnp4rG88rlgH01*KX1}RV|L>=kb`!93MZ6_n$e1)DKE@GRI$C$?JNy4Sg?@qJua-sVhIP4SuzSG|G$pYw^gxk@H85B>(HVpj{NPj^<}%D~?a?OZTN8vxI-AiiqLolB?eQ{d>kU`kt<w9zecwm49DR77k8izcc%{8`6Es9;2?%`Z{@#&Pna<D&(s?29Ylxe~RZz&+9zDZRvgK*i!QKx1Q7QUb1^lidPN{;C@WokWTR_v3DuYfky1xZsL6)b02+9(ed-HoVJMKH7SQVes37fYu$s<<Vz__$yaS%!~0Hp))V^NgJ)^fZ=sd>dr0~%@|F9S$X7y&XddYwA0uCXFNFP7MYIp;o;As!&%N|d7ruVQycAw%)yP+JhLJC6=kff?%zaAt@#5oSs`F_g{|=NbWm28*&Sa3E{xkXd=S7r9DxOZhlGcLH;pdk)|LcsWlwXSeG+4-sUYw`YJ+r*8%Wg%!zNBFVU&=1y`ip}y)J_$C9ZrbxeWa;lc+1eLN%bXP&vHKv3sd}k)xZ8}cxvze>Zjpe7CrvopN4%6HB2+K05rjKpwq!Z{lSigHo(yOq6zK}?E~%({t@~U_(yO%Xcurha4Tp>a4YZ+(AMA|!1bWb!S%r3LmPm<2iJhs2iE}Cgf;}%1lNT&1=j^PgSG)T1Gj~C2Db(Gfc66S09!x@f-S&m=uog4JOVlzJOVrwZ8XN|B=i7uH245`4Rk1YD6Y2#O|TZ)3#<h%f_4Tk0{cPRfc?M|piRLOz`sBnf`0*zh1Lg;1&@I?0FME?LYsqK!S2x3V0Z9DXh-lw@MJW>GoW3-LVp6!0MA7eyb#(4EOY>PA^2}-f_Fn5!Mnk~p$VR8Xp^A!P)D%PzF;x#VtuYh6C8{tcolRScojGZ>I)76FN6Akmw}f+y}?Vsi=kfN#oz_dN#NN~7w9Cg3)l{754HpMg!Tms?GEk<ZjUBd1^p2$v>jLlZiFVdHnbI3=nvr9U~_0ausOIY^m}ksa3yFBa3!z=ttlD*1e-wXf=$3xpv}Nlz}2B`!PUV{pgq7%z#X6#;11y4P&K$WSVj{(5;_7r5<CSu6+8vJ1-c%5&Ct#nnhs5HAT$CT2p$JL0Uigog&qRig8M-?g8PBHLFa?Jfm=eygIj{@Kpnt!z~4cw!QX)^Lx+GXgH54UU{kP}p{+19PeVJ8CO8sJ@M)+MSZIInX>d5SD>xh+f+l!5v=dlp3-EIAJT$=`(8ge)wZI-=XJ|FBGk7@E3~Yw`9geXU<G&BO9=s2{2O13C1KtH)1>ObT2@L}81cySGfkVNYp-aG<!5g59!5hHqpbNn3z$+x<{<Q*aHpWV*3)mCv1hoS@f%`*yg8PHJLfeD8f;&M~;7;Hc&_>`E;KtC};KtxuP;+oCa5ZREa5b<Qv=Z11Y>IId<2nTzC>htj;E~XAl5wvPEJJN2<K7~;H?*H*+<ydjfOeCN`<37((3X;Me-m6CT1PVOhk~m>zmtsnr(hFkWy!eT3YMUzU{l<?_=_^M-wiDWdLOJn|A5{H4>L3yL)#180T%N|tp9b;Sjjlw1aE-GNyhmpcr)~ZWSq}}L!lQX<NO!A6Ph3y*Nfm?&?L#Yz69@qrbx#1D0m<Al4M-Jf^}$u#U6hfdJB39d<%RNngYHFz79<SUk6`>CV;PkFGDYaFN0H|7r?3DWM~{X8Jq}>1t)^zq36NzU<LYh%x~a6@07cL!RPQg8hQgP+8MkrGy;4Ad>ncPd<gGthaLxS#CuDj+rgq~@cu^deAFC?x?{j+p{K!T!Ka|%;8WoJ&=Bx`@LDv%E1}E5Lg#^3f@h%#c7u9=g*t=Xz{8-!!Nb5dP%E$vco1|5co6t!s5SU!@L;F|cre%!Iv#8Z9tE8bo{xSOoMmVkhNedooC!?_XM&$VAA+BN9~s&M=soB|@B`=_G{ItSU4h<(-UHvmXYZm3PJ^a{)4-3R8Q{m@r_e0$Q}8o1!OzhIXG8ViZ14+-zx(`ZXse+I!K=ZWphv))z+up1;4ttu=uz-C@K)$yu#<yHrTV7->0kGZe_C+}RQN}}Z$DY_XPxq&Y+?Aq`tKikoE$2PbH;FRRH6rjIB|MO{{j%wn+g'

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
