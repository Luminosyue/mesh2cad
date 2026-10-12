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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4119064c292c4a6c8fc6236a8034c2f1/part_003.stl', 'relative_path': '4119064c292c4a6c8fc6236a8034c2f1/part_003.stl', 'source_sha256': '7aab14d0a43e06f6897c368e1c8a61dd49d444b96219241b668e13223d6d3e2f', 'input_faces': 280, 'input_vertices': 335, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24600015580654144, -0.3917175233364105, -0.19768935441970825], [0.23647622764110565, 0.2835473418235779, 0.2859131693840027]]}
GEOMETRY_BASE85 = 'c$}qL33N_Z*FG;nf*>Vgc0-61l@N*=t~nAalv3kOi54LeLCsgGqBS%z$8gaYVxET(7eP^Dz8H(El%lP9=%=mkoc-*s=Kkyd*ZSB0XRW=SC(pazeTKWwKIhydIx4SM34xzLk-aVNjGrqCp{%edAx6X|CJpEtJM5hyLq~Z;G1Aq~-<a}#m-f*gdBg}YCb(bhu)c}G4YlA#{p$zU(1QENCnhDv4Cxb}*e_P;tz+Vb#Y%nHr!hlg<?q$%)TvuTs}oW~8>jsre+tSjIKPcOb3pZ_!-jN)*1~#Qn@TiJjw0Q3zTTqHUI|?*81K@pULT|=-MQBsam=h03bhk&lfTuo9`w?OcaZ-R=wd^4m+tf!OL6Rd{ZErV=fQl1`op?gD1O4nq?;$&?je0f%>@)cxES<lK_?U%2l~vR{_mV{isD3JT*l1j2bHb|jwju`&f|LXlyvLmhc4X=NLx!76^S@wFfRS+4aA9P3jdPmzuECB=|<nmE`PIqCyJxTmvZ@w`b`l(!4Ljv7f#YV+$crk(r3N-o^-FbmeBZvE^Jn4w*HfJv(%Bp6gS`?+AV$_{^#=@CG2)|4aFP21p4mqc{Klz7m&a9Ln`zW`wmi^XVCR+^PmqtMe{6X7!=1EJR9vcEcYGZl@CZahmUl{x0lp}f8%2CpNi+AAD+0HK7X;F#%W%CoJqg?My64_pY3$%X3s`=E^EGV=^|n6D*F9YJn14LDV4@kpd$L;LnmEtPyp?ZDNp{okw*OxPNYHeSncH+%D3}NUAh%?!luvXL>?zSd42}{-aQogR=gqUM)!^9Xnu<|fPZ`_=`w#Qul0QfjY~ZBcI$UPro6DO?WcJZI_GEDrsMP+ckP9K8F{FsZ6Mv6ycGKAs@W7T`RM_QfA|~d37l_nUy;9=J=zt=%&NSP`rE#f%U`s=o<VwGN78M7&Z~cSra0Q82t02;&f7_+$zQDVC0##*eA5@kk*=40bd1LHYn6Y|_vXY>KkZT%k0I}oKf=q8{EhJK(7(C9pZxBxM!vsX20aDyZ@0^DQU9(jhCYJpLvma6Gi?a;DabdwhOw7$%Rtig>t2TllcF%s&3e1y*h!r+4}W$b-8_UkV^%XsxBqxZ<Ft>xlS6*1Q!;7(r<`-?A}x9ewKJeU=4Cn7wb^$*#d8w#V}0H|P2&}VmM@}tsJ{IO>Fr)q9D76xeQtd?-=&)kLl=_&#Zc0<kC2B(_|c;@Z^JzBfBh-trDM-qP5BV8F^k&&jPoa{C;8h`qe<6VZlyT-{l_~AL&}q`|AOaeH@kC$`V-<uy2!?Q)SGF@xBU5_PsqSJyw;K06+5yipKNZ|Jf~B9BMAE6aqI#Q=y_?Qw?khYhx`u7PNsJ5ZGpbz$Fmg2>a~mfr;JDZw;o&|ecCa~7j2V)JT8uW7L|J*LO%6^|M$pSb6{7}wYR&%{|DrWvt>By;<yO-AI0-Ei`A!jup?U{ZjT_EAAM>htq)^lDB{#bo*Qj6#Q)@N_@C$TM%AbFs22)w#W%A2w-NTdOy4snaX#<eN&PW5+Q{Q&$SWhV=l3+;$j{t*^9?rrzH~U^@N*G2YtNw1D}-P^7GT|(%bl&%&x-k>??Js1yQ65H^_ah?eY?^f<axxREXs%9PP=s5FNf-laX20G=l2ljg<IDsj(uSf#<830VV*yZQJiUpOBV-|chhs&*Z3gTOAzw5tcT(_f!k<&c1Bs$nNNPE`M1}+q4~9rU_Q0Jg-}1Ip4?A<e_>r%*R#<7-!n<K1JQr;QWo_`)LiQFcY5DM9X*tS=ayRKJo$xI?MC{|v80R7d7gvwQG9dtC-C<}eu~)chbez<2D<#sjO5KUZ#yefz0ug;%K3x*jm;UfKAgGQCHlPNA<9D$U54h#?2i4~Zq@o6t-qLyG*6-n>b%ji3+mnQdC-euT{tbhQSbVskZyj*=Z9H&Nw<&m!1E77KHIYnqTcmsi#Tz-?+;#sde<4cY2#cWepp4icAyFL<6Jim9zIL+zvUI`O(^fzT^5lpo;-&>0r_w4)zPlkjGejT7)b}I-s#?LU2(*Lc+%~ZRLTo|F+Z=!@@e$@+-6v>_g7LqaYAaGq5f#q;Qt}l)saO=cRnqPbKZ93r<L>9X?kue)3#H4BT(P0;6&1e*XZrJ{hfYwvCi8TC*8P*x@y!vdWz!sHlcMdvUnf4euUPw{xW@QZe1(*n(|(IQI~W*0{eoc&p4_4wXAgHDeLC2@dv2=Crc^6#CFtGqj@^53nynh>3Y|qlvn0EldwNt?LoR(6nUt9)g5*IennRtJANDXP2a#x<o^ZdbL^n+XdVjJ*_d0`d)1~qH4;wIdC**f=c4<(PwPdWSKOtWS~$+>em=DCiROIH`LR8ntF-mI7m(f=&r8oci1Nq$Wf|#a4dku<WCQB)(B{xbBd@e6Rgl-`Ya>n)o}*Sjfa2JbmeKjZyo=|h7fGUg&>qgj`C}gHt>t`9>rPuRnsl)a=Lb=x293ksP<Jl<UJB<8V|xP5K~Gl9$sI>@t%7y>rVaE%yf4@js4iRC15>C!BM(vDimI)spHA!(?2{Ex$DGGLlvn!4)@=Gd>*D)h)Y%&AX3@BlQBUkPGfz;Ql^v4EZ$Ix-6)z+Hz=gv|--LWNI#tCy6ltDF@qBsz&HEYhr|Z*?bNgEl8d3fmTiQpHJ{|dBH2VEG=DE>(q!+41^;YY0f%;<(NUurbSjOwO;uO@qMx}JZ0t3ij-(L!K<#A?*rn%zlcPdhyHLqOg>56k|9IZEVPR+j5&PMdpJ|0ZtvbPkEC4U~5Gkg^Ce?m-RZrzM4kNjVeI-BB_=Y6oGAJ+A%Uz2G(tZS<^-sfWJzN?SGbF@6mao$?ff$p!SjpuGH9f*3eY6<Cj3i8B`{t|UQq2OG4K0hHptpellT%JuQT~Fk5*V(eDw+*xA(fByNUS=fal|8S>eA3V0{G;7zL;0z#oHjpqyUvJml%HDKBGSbjZujtXoNsR9UT$)`R+Uy5m!~o5VkDnuLcOuR2P}erHQrzPw?jP$u%UOtx;Cpl!1;1t^VHmNv>Ijcy$c(lhaip<zmm{Oxkb8eV_&n!K7fCRN2J^Nu@71`AE8dX3ZQ$TSkCn)B8KXck$ujkixs}OpXJouNPaVsZ&snnsCySHZ_2F;KM(3&+YHi0A>@yqkVJW<hgG2ay*P@xswZbbU)P;<o&D|JH*ikgJdSjy6Y92otPbU&)nJJ$jyO9W_qEw;={<_x0{epDpHBOQI22CrV@%e?iI%iq7+Gscw=?;^)A=^-N7j`_+j8rA$`7<3Icvv|?%d*iE$<!5f3ePIJGDC$`Cwd0#=cq0pLB5>{#y5|v@Wy@W1z3)_1Ij)dJLP2IMK)l`&BLM%RgGATeq=~o7wHpVEwNq-QaeuD^qc<eXsluSNxa7QI}qakZy8(V_{{Sj|R2akvqN<)eL!_unlo;2GY2NPX}6G`lZO7)ZfZ{4w<qZ`%%4U(#;jT--W%zdxOwkq>IVF(fb0s<Q~-9+7n&==7PT8Qu}kC?Zmo9{)?0TR0phy|8}*j^^U^%XRyADzQ2j<`L~Oqf8A>r{P{jUqzlC{&9%E+@tc>Wb>sAYgE-r8t~0Niq#Nt~cjt~{4oSs2dsUWnvnkG{&W7bU2Of<gU1VTATK?B?4-4o7e-Gc+vTh<y$W-V*AHun8P-Ut=&h))|Y1}ihe>wBEY(qO$=>BK<aNRBzOy?EnXwiKXhjshtmpE64Xrzl|UZ<;TW4({;@AB7!GB;5FL&muL&5U<(Zhz`e_b7cOKQEt$nBRm(E?tOjz7%h5B<@|Mu`lRR&*<LaEL;Y?DE2k&^=0ahed@SN7v9^c{y2@N;622CUXMAAaNnsg1?Mwv*Le8^?*Te2f<6QDCc-;m9)77zag95EmuWngUmhaA)P-oTBj0m3E=B!mdJg&fKA*d)SD|`hmAjAqcq`w_x{k$jJ5U1iH3aKXH}~WH&rW~Ldm`_H;iG8Zw-RHZr(vC%O~R?Jnzxhq{Q~ZTV)i$5?za!5y8R<6(Y?r+aT5AHtW)#Yhg8R$yJtwZOYwf4la2dY_ctzGdl5tPta}%r`7pob^ZcIK^t`l{-ANa7c>RVKpt@&8kAVLi<caM+mhw{68b!K3o!<*-3#dQ#i<vHe^Wx}f)c=%&E`L2P0rhtCCA2$)*J(bB+STGq((@GikPr6$;dEZoG6SKDA)k`I_!_NCt$)zr+;Ob6qfm#B)xtfsBJazU3Q^rQrZpkm{0Vtt?G2*!pxtcaZg;>Ux}O-SvCzGF9nEe@{!Z^f&{y+&-DdkJAI!63UF~Y+enh>QIKdT1j9N|SSKV)tOE(`?OsDyuG})!w!=|jFe(E#P{|<cLnehqMbJyjh>ql|^v3=jgJXBwg{_Ny>m0k+xqp%%_pN)OiiTRS^SieFylX3pHUUkPkc;XqCzsP@)&gJ^R^UzoEy||Bob7tvl&>hr0``!n5FIDCt^nxAfy`kRd8uB5;i}F{@MgC}QKA`i88DA_bcYOQgKw7^dtQPcF?N?GijSRf6x!aC(ErHi#+je+A(<%Y}+BSM$ZSS~+=aQ2MeeyJ{lS+7A;?^kC(ZPJ5TD+9rH;TBqh|l?>Kf8+aO4o&0e_x|6=@Sm&oHPXMQtZ2wj`;QVBVTU9za;JpBGnh~^S`(U|0a`g55Ccl{H<NTqd)EWJo(xO?|GsZ;C)_GKL4z(K=srP+Tqg8guJ-dRWE>Xls-fC*myFU{Pkkhp#R2orj9q&D`QL(=s)A{IO4`G)UjXALeJp)U1n9B`!-*Iz7+Mu9J7%8^}Y{X{vygNmFCssPvg)7_<q+e4f9#GoJ-fM6<9{|em)xGo{9W)9`k#Ef_<Q`xKHDB0_GwQXAVM~EPj99Aq)Al#e)BFyr0)HbCB28M(FVeXnvfB3Dh5>#X0B>|6QQW8?2kq2+YS7<hfDqJl^L|?TB-9UcT>puHc@SJ{<mg`F+T$K6H*Z!p32q;*f7*PXylcUG>5DEI#kep9FnEX`HXy@!xTtPlFy&-Q_RJYs;x$-NIbDkr9bHbEdXSceZ~^bw-4}i+iwxbECd#9`?m3{QW_kz`R*2kJGu_EIR@7eS_y`)>+c6u?=WHv<LA$F6KGuV!;=ri>JspyG0PKd#B4>(v5hmU#G`mnt!XvO~i@f{C`mz=l+?IxCiLNaZh?P0{f5E4f-0+!{cMHj~44kx?P6Px79M~Tq+A5>E;sD8K=Qq+=n{sa_Q#lR`mW&+mq?i?K2x`-t0{yXg?IY>&!!*J;VO_<$UNh`8}t|i~Vx<V(97ocg$s(^!Gle*$e1i#cAE?qh@2?T9(GWJcrMdWg1W%Z4K*_`F+lHFU&_+5biO*A4VSDXpD2wTanP$V}6XUlks=+D=lfC)NS5JPA^Gq8twWof#*HLzp#8|6ViM{3DG|$*S`oTQT_al|NXxR3<&>U{fj{D`l0{de-Zdt_Mx-17Sft9wr1?iyfyO}HpOEZlb9=<!d&5G<}r+)GfrmyIrAlKiZ5kc#$4ep<_h;PU&5HlxQBTr^Sf+{|Hycbxx(Ab6~1PEm$9e^_?o#g#mjqOiWg_R$6Vnp<_dpjuKX4HGAiAde^>kto8k`R8RiOiGFP~p`5nd##@);_n5VKSzKC%#bA?|pS2&4zD&qvkNz5lO@59)ad7!jVX<=-NH)L$WTs`+L0=d(LwbqPHn9q<lRN8zt#Yal(&e(}@DD#TaG--Z}<(XHK7A&nXo8nCw-(jw>8S`Rt{#!_Uo3Rb^{PMHB(n>HEW?q7MZ8pWLG5RpC#=MHOs*D90eVF?)da)_)Vf10{VJ;X8GcU}2Qa{zDg-d&jO>uuV#mh1_XKqP5Ds466Y3BW<O_XLZj$<A#ZJxAG8D}z|&(9;7aX52@BbX;MpUU_d^Qp|gVjRs};n&Pn9~N*w6s9m&&nJ?fk-|{spUBTl9!G!X6B*|+pUbfnFC@QnQDQ#Ee=%2c@|fpkv$Rdpav0Au&tdNIz!d+JwbRW1Wd3i)$IQQzc1+qM#$TD=kme<0J!jOI*OypNS`=e*=F8=0d!?;pJixq;{H&I=MvU(<uP!Z2T5HC3%vD?7+@8W}%rDDWKS(R$0s48s%SbCLEf1UG1sT1W=V5#xV2a=8G2Z9#-Dlm4eZ85hzBct>9Ceu2Wo*K{F7pQLqkb>Vrg%lh2FxomFUh9(O94|noV6y*6~4>7fV7*^FOcyC^Y^7iNNdHWcuU3_%oUbkeocOFzqIR&`<ScTyDDuR;|}KEOFJnojd2Te^}Q8Bor#1v#F);e__vHJn7<|4ek0M}15-SJv7857VFl(2OEC|TJ~h-@VN<-Qv{vf7(&{mmWL}a#ug6$}c_Wp_(z-E5Gan)?N?Iag2j*%|tmOG;pH=)FX$=``GFD>VR$6<H`nv<L8S~20s!D6jRyEgW3WFG{GJhr8ekScK<0<BacszO76wk+FFT>+jSb%u}{=6h(QRa1}y)CU2V-e=Mv^LUOGJeEdVNd1?dofqop7|_kUrHOyIDq+hX=A0$Vf==<%BAC+Pg|I8WIV!L;RfbUr2QuCA>%L1)jG)Q!CFul%-o09ObBBj^Fa0qVXVzu)tV|E)H;QK3Gkn!{VY(|6dq*0R@xeAS!{|Q=Fb(bVqC*q?HOYP_A-UNnMX+LC+$7PuFMs-W3KRB<{wH6lGZ?4O=-2H6=zdCfUyqq0Oq9`8!#`;yaHnobA^?eD=fxbp*M4H{=VWLNb4wV7-K>%{yzVnz&uW1tql}dXHm@CG7e(imU$#&9P>Di6UptWc6zWWK1$j`#@UR+m=EKA%w|)3I%6Djh0~a?m$p?}Hk;xX7`HLM!2FW5D~#J2w=pj)b1A<EpDR=R5`R~r;NO+5_)`fdr2WB|%{-gGqj+?bCr^pI|I@#K|MO$2n67^a|F7S4Ukh`8v#KWkxg<tM<x}TSS#<Kygn87-Rs08&Q40b'

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
