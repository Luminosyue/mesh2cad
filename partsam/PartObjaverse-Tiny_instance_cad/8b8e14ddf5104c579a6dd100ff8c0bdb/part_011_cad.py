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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8b8e14ddf5104c579a6dd100ff8c0bdb/part_011.stl', 'relative_path': '8b8e14ddf5104c579a6dd100ff8c0bdb/part_011.stl', 'source_sha256': 'd9c77da41702cfb3b8dfc37b9379fcc859a2699b8a3a715e92a47fc2bcbd57dc', 'input_faces': 384, 'input_vertices': 264, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15081927180290222, 0.21337208151817322, -0.08418648689985275], [0.050639890134334564, 0.4595361053943634, 0.07271888107061386]]}
GEOMETRY_BASE85 = 'c$}r033N`^yT(r<sESrm6iGhHKPf2@L($+w2@)jcn!kulibSHOBA+>8o@tOT#26&zAtfio7<0@@k7~?G(N<LrH~V>?|E=70?^<`=o3-Bc{Jtmqd-pzjI{Ta?D4>{A1x<dcYiXBGOwvEmG!@QT1#M(#%!tU4(Ac`eqQ^LBW#Oxzf9t|d-8%;La?nO<-?<M8jSY!$Z)S1#32Wl+X>kvWiWw0TJZwNz%%D)^`vnh)4K4IzBZ8wt3qN~!H*V-@Y4Dk+WxVD8`15{Y6O7WG4rdms*=Nh8ma0vgXC$c4mhu7Ohi$$Le@T-$>a+H|27HUt9x0z0J57DIO?DAKDNV{ZDK{OTUCP6^mrlN-eA|?ic_`nkq?B*9^CHUUUO*oG@YzGC_h&==9FK|Wvk`C#zIFFp<k8yuqn*a%gYfOI_DOrHN1&aSUk|{y>{=)7$?i87`L#Xbug}PZ@BeBNzF#**@?4pE6@I<!St!4Ftkm0clGI!BB7Eauq_nf+p$qW$o*IwOX9r6DibtjWXHsXN-+EZ3{F@x9_r3YwqP}Eb$v^(cdH8h$N21=^Eu?&0A8AjeC+JUOU1{<AUy^#Cgbc-J&r;HUr_6Kkqk|$)Z{Xiq`2G3j*Wlmlj_cJ1KY?%YJ}>QQ-gFAeS+2vk_h=&ZPOgb@(biv)JkxGSJ1u{QU>yBVz&CX3S@`LL8!FXpJK*bGtDJ)WgKsp(f7wRKpL;>td9G(~<V{*9`H$Ty(x0{+t0e!?z#O@*zWtTj{TEC7zb+})WlI}}c81K9^41Qg;b%y_mbY=zo-*N*=SjkV%y)ca$#7}Ew#y0abP(Tscvr4Be)(wRKV_BjeL6}0W-UXZJ^M;~9IwlDby_n5*ZD`Fl&`v2>OC7W4*la>U;LHBq~7~7j@Dy!rC#%_^#3qN%oAIe+ERYnO37n&MgJJR+@(Kf-H?9x;e0sC->fCq`$x2t?{Xss`q)kK3~4Lv4|?7f<-!UK_`jz}dHct0(a&Dz;G4ZxOaAn{PUwe&C#8Iwo|0!mk66@OcO`s1=Yiz8&@URk^C<Y%;BO?)*JazIA1cO5`C_?J{;w})qI|`c@GYhLUxz<81MN3le5Cw|8B*`*ewfcTOG#<ZxaKn7^kdjJEcG0u-m5hwPxtt-$TKw|6Tf#WKznQjjuWBJe?N#ky&p>c*vn{-`T8k*Gy8?KU;hkww4`+SmSu+I@A$<m%(wh`l4n$DX;0lH^U-hhM#8tcCP?|ladT0AS%8$ctvU5>KiIRHNxc<%qr6ewV?O$=?2ZG-vo%ukTwI4dT3QTzyXOV?`iET;@x3#l@J$!z8@Nud557mek9$d;KbK4Sp@UYypSkS^<Z&;Mdfi>tLT}82uRF(_L7ocH3s5d^7JPGND$3h#g`r-XHc9-rlafdK9C>VAt?;e4YN0)r`3WiTYn6s?$x6n)ZA^6Cit!D9l7V^>nqnW;kK}Ade}23Pz9r?7<d6Fcd5n5V@Qqv-8ONk$xbNsuQ{h|7ZIk<j$Biw>|FVOW&nqYWf2Jm`OZ%V=e6#f{xvs5)x1hc8<)vPSGO|wH95$l-P6zS*p2<G&XH7fuXS~@Df5>AQFW-8|qt`tL-*j`rywbg<q@bPM4e=vVa39eJ)WY@Jf-}S~UmN{qxDDMb>#~9P3!Y0qJgp@DuKH4Mqa2y%XT~JrI^Bzj|13@Rw_;1A-tY(ekf+va+!t&Q$IEq9v%|L!O_crl*AeUSIkO*py>EByW40z+m!q8}e5HKtZ{&K*pOACK*j9VtYu?iS<V)M|y>Y(q&EA<(eydLyG){+aEg6FH_CR-(*M^vTkmsX1@U87?OP<Da;2WtYFz&W}xr_0+?R5B-w)Ie6Yd#<yzwbO5zIpJCjBmN(i_oqg{l#A;=Nao?j@!`>58A-D`t-s)w2q9}hU?$_d^h~|-DTXL98JdeGYjC`z3NN<yS<l+JZ{IOyu&KYLo@Oc@|Ygk;&+wtwMS(oWBh&hOP<aa%s1obqgWUADg)u`3nFCR#*D>2WBPQH^8U|dze@Ub4f?@wg>TOO4)e<N-kFZ}bhx_<{d3w+#-(ey^=NPO75Mh1budr#P4i^jBV*v3S&OCL?$%$1ai0<n-`X@x&K3F3u)fUXK9YZNbIc#(@FMhsbyru(<GTa(>UU~vN4^|?$>Y)+zG>aD3BNB_SA6GS*~fa!!8$VgeJFnOaM@3?&!wUK`lmZlZ}bq!^CS=BZshzdev`>Ee|D}!z4k|!;M>;>7eDDT=9S(q9lkl>sm#xl9Y*1LyR?RH-TsBNr&YrQ<oCP11OD-Wa$Q5eS%u%v>jU3@WW2Pq`8e5E>sNtqyf;eD1HLUVe{6TpVcwZt7Dyh~dK>Y*#Od%Y-cdgyZ@sm0y>I(V`8um*o)3JOitG011YduhD*N`m3Q4H1n~&tlkoj!smWOs|VU5JUvjy|to;ODNE3K0Ft^3J-b!2rKuJfKI^(LfAzin@_71vep8uQxv%n$R{{Q5_H*4kf_`969&=D)q4^p`F8EPTs^YPc?KLn6k@8g?4K{m=T+|DKCB;QPBbi(hRQ)}8TjDCVc0w_Nh%9h81M>>+sug-Lq`eJ%69SrFQ7TM;Pb&mETh6?4%)=1CtZU-O#e;XY%`dyI8sseKRY!m!T5{%py-CjR~E(*LftaQ?SvU4?Jm>n-ad{5bke>y;?}H^Zd7$H_5h*N>s;vW^pFUX?4q4E66WBYxC=S*Mk&twH(ELy^z^_O!IK>8^FS-qyckpD?Cu#=O!WL|`AVhuxL^Bju3vvxhh4iS}j#d~21Pl7HF|%s2f+0oJkIJ73n(zN08_sdQHS;hcwopUM4kQA7CFQ?Fz`Ot}N!ezmgrOFU8D+VcqJi7l=;`p<YX7VR|pmBRhVj7-A)$8xxo?5k<h*S_o9&wl}5PwBJnUEl1wTK22_8e58#FZ~hv-x5DR{axQ0>4W)TUlzQhNFLYGn4gvxzPpO}ebccn%oekY`1bX|SV#7bZbf`ccqrz-^>vdX`K@awV;xyWY1@kA$(M7TG57kWBL1Fx;wQ%?7s+$YSLRP*(wrjxh8g0&DG}B3T|d~6@$Kun_+8)f;-So+^UITq__Jjk^?}9L7Rgiao{VGOy7lk+X1DU<KP|hdNcop8@Xe6Un~UVX`4xO4`>&$DZL*Y4e_1q7_zn2_y)ql{y{heSUbDO(c@v-S`YptDH&};rv@t4A=D(jm=8v{2R@UW(*OKR&kDN=3%liy7$QyaIXfqh)Pkt(XgPM}xf6-F>enyF@XwRqLN;^MrmUGwN5Al3v9ll2LcPfE(s#W<E&xK~X__mIvaNgElyT_oNO+00P-js@SqjvxJa9r0ZFO;`CIpTUX=SO(1GPUB;POtc3&~6ikq29Y$vaYXaOOdCC7oH2PQ9Wh99oroHdEtZA?*~=>nq{OtpR}>#d)X5^qnuw4Szl*A!M>_F=l7EFXovM>+Z!S0@Da|zn8)w8!u{Q>6Da43(HjQh^PHv9o?UaNLiZjC!ThKs`+%)QCmEOQ09=QqYG15JYvKzzcU>7M&+*#=W&Pexk^9KyQX}yB(pJfTA{*~{wC(rc>(hBZO^nCBr~T_9p1;i<C1k#N@0*9;>y0O)zAbLD-xl94=WWjp)6ox)dP;t;4RP?>jEP5{!>)2Z^qwjA&D-Wow8y9_`I9PRoodmy@LXsd{!PxM&Z}0z-@6pgZN{=_+4sgim-2gBp<UMVM`itbHtL4&HM<GlY?z0A!``ku`oZSW0nde&_%(7LY*PjMq0M*90{9!3%Xp=p!G5AOcELH<nz2~UV}6b0IjhuL@#FK*|CWc*(*HBPu}@f!<VgRNsUhdR7W-uXsQIbv4@s{vPi%9vC1{`XLF{{${naE-k2v^d+pW2BeX%l6Uf#fZGH)-H{WG_fjPI9!;l5`EwUK_<-X8D4Y@avBy0N#OCg+pDvQqx574VI-J!Bo3CuRP>-6Q24Udnkm>$J?<LH$>v9kqUy`+kLe(*MU-!nbsGlKV~@H;k99cVrU$m(Rsd-M$*@_N%s7H`Z56B~Qi>Ja^c7t%GkFeOvBF#a3cmjPY;b+k5%R{iWnl^n<O!0_?lS<>}J?(P`M%j4c_mA78(W@zP@|VjT5B*Wg=wUy$bl*Pn2|)7y7gE$i`1X{YlHjF;Xr2)=dxZ_*FHIbq!yP7(0!x1M2K^!-W5W6X%ezNO#ThxTaNP`v-t{3pY=B(#uuHL^7NN6*>4M%F{Bye|#R#yMY4IV$C2PD#CGyjI|P7c|22y7gc$wA0qF#zNGaF$=zZ!T0hWAa#}G3D^%`fBK8GXXR+Tx3tZd`;w)xmpq?NeJ100vy=EyA@ZF2=qTocp4&z4V;f`9|N8Qqm=F3kD}3v|Z>8UkO_BG#dyYt+6_3!*wuz1yM}4dx&RLcSH}soPJxlsC+F$%P4dgxWwa2(`*&fHiw{MJ-ek)Z5<ExvG#UB+S?f>oq`bV4n0q(2T$h)Xl4=9HFg7L{(@#l}1_K$BU`{#)J;%}LVJhnmom!N#BSMcqXN1;8&g^f60*{V9@eqwz%Px`sX2>8bF&*57N2FrCF8ZP~rSzpSZ$dLCi69%EY7WspeZ!`n#vE8|g^RwRj5PUOiru4(^ELleZ$Hm_`P0qtxT=8B)KX4xBP19T?@9pz{mgkhw`Qi^bhI);24egmhMgICSrpN8^wsPvItZAjR3R+n3JAZmnruzA}{`Y@+iEQ}4`qN8;Cjak0y)-Ip!xx3&Lv2o0`W4xStTPn1rnV!uCI?cxl9di12a@|S6py5iAkU)CppGEVAWx>ok|&cVP-Dmw$m6KP$>Ydlso#*5hLOjT$1oI+rdr8L`;bSIM==x+rS>8ZB}Y=bk(CCKBgumpio>ZL$x7Rj!^s1we&m7VV20vQsy|t2XL2ZcFhlV$Y7g=-aul^EIf^`l+MTSl6Ip2pc?kJChT{IzugU$%?WwKE?a5zK8<UlKlfNW4pngtnK(5PBT!&hl{28?dwKiF4EpiRAg`v0#^;5Fa>f|cqN({y2s8z{IKPHzWf5=c=g8Bhj>3if7WJiYLV$@P(rOxDH<dO`<A5klkKO(zO|3!8ods6F>J;@EJjmS!U$PLNO7>Zj^b#e=`FSRvUX&~8`+<~FEH?<#G=}2;K^0y4d)3kr~8pX?~-&1FimChi4PhL))OkPf2N}WJnN?t-8M_xi+NF7UFNM68DJfAv-JfA#|I+{F>Jcl}ptaK=O4tXXul01_<ouPOVbr5+Hc?vb0JcVqd4kX*i6RE*urJ>}B<f#nB3Dm*l1oB+!F!EgTY-$u)=@9a4ay<1ray)qvLvbQQaU8WjIgT7bZBLFM2T;Ex2auaG6njw{kd@XYdy(C#b;#~yH-_SB+CTf0;!mhGsh^RR)*#m;yD}74rdr5KtB@;`%QF<0rB)&<Ek`a(F2hj#KJ`QL`{d%(5@e;0<l<zFT1@-rN3jF7B-w%NME!{DL@rHrA(tjspn8%kkUgjk$sXkT48={T&B#s2EvYTYN`1*K$!!>lyHGojyO8@*dy|!ZOYTdKrcNVAlgBd@FV_Cq*A_DrZ)YgpM*W_=jhs$hPEIGMQJ0d_$XlsP$Xm%<s0+zk$eXDP$eYQj)cNF8@+Rs$@+R^|>KyV$@&@Wm@&@vH>U8pY@;d4y@;dTb>J;)?athT(P9d+MP9(1(ucl5VuO=r`6UfPAJ9RGEPEMlECMS_sQRB(0$SbLf$ScV!sEOo13gfTBc*IbAkNSeF^f&T7@-Kz)Gc}+38#$l+J45l`48;x(qA$oVSf64Qir>=vgZ!5Kx-j+?#{R<C!%%#HnoU-EihO{4oO*?PoP36%_$t*TUnT!UeMtU^e4qL!`98UT>gXU`Kz>Tq$V$~UJ>|9iL4Hckqdp?%kuNh8U#H$9UngH;D85Mjg?y2m`_5P@K2aE1g>jCWOU`APa}33|8HyiJ^U3)f`v(lgPZ)}yGZepMD1Jlzo2*pLi8uVLxHv<x6IIO*C+cgm6Z^K9gM{J|RMqb#I1Y~F66BH$#jiMCYAj!IOdpb8k$+_<zC$(1Cg;-~hT<O?iqBI|k(FkX&y!Cw6dTn2WTpGa2Kfhu;=K&TyQq7}yU07J2gp0fyBUfPQje1ll8;c&kdKgas8`8Ke<J6QFHrB3FOaWM3&_{VH>gj^H^?`sdE}eq)6~o4OzKhUW%5z-G3s@)(o5uH<ipg9<iq4c)LgRCEb<}pPU;ErPI3lA@mcCQveMh+v*cUU2jpAiy9~vTsZYpCpOYVxpA|+>fP-U&V*k^>4*&CGQ){KjKNA1fZx(&+_3k$(6z2NRmta8w#nrj5@Q~+-7cfoLsZ0A0{ymA8'

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
