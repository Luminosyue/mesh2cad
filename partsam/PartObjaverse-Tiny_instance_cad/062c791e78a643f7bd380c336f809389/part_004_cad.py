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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/062c791e78a643f7bd380c336f809389/part_004.stl', 'relative_path': '062c791e78a643f7bd380c336f809389/part_004.stl', 'source_sha256': '7ce5af0af3eccea35f20801e1bec43aa4056a91ad258f66fbaacf06adaaa81c8', 'input_faces': 595, 'input_vertices': 379, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.36705633997917175, -0.3815133273601532, -0.295077383518219], [0.49857237935066223, 0.30191904306411743, 0.34216803312301636]]}
GEOMETRY_BASE85 = 'c$}r22Xs}%y2tlWB}!-k5kwBXNC%~p0}4WDp%bL+Kthui5~>e5_dd}J(gYC@E*udNV}uYwk(NUsKnSUTK?FH~h~Py)L8T~fzM22z?wOOj)?4pot#AE*`TmpHvuDpf^9{)&yl2s3A(s5AVVxiK!=$HbTNcGLR){q-dV1W1G10M2rc9f|tg<3cUrJZ@8Pq#Gf>|@IH|s@3$Bvm^ubr!2hp}zyHFDJ(J9T>8^vEfrrcRHFrhK=^NwLv9A3HvBS~UN@e#_Qv8@XCGXylsb`agaJ@gexXnU^2R)&B73{1mRfq3;|{DI{;L{r-5UBk#THEwsJLtM;y}O|qZlR_C1U&Ai#(lQt~Bu=XlnFrE%qMc&mhQtRK$o9%ran&cPOUgcGL@9k#i#Lw-XsP%8=&Gy!j+WCdGSNVeR<j)m(UynZe_>H{T-qoygeqrrZUbVOHZxeaXq6%97W<H?(?KkraZI67x^ZLyv@9W@k{dpPrg88YKd_mmT$VEAn_dMKtJjIc>zrA!ye1G9qhBNQ()cK^i&%8HIIrF}QRnqBucYJP^Gw=G~-Vt%#$ZI)T|CM`-@p(SW(DJ^TwNgYrJu}ytx8gtDDei0S$~<vjuFe<5eat#7+S&8xtq*nNeY?^{-qU(*oHOqUJ1E;n-27b2ciJGYx3lI7XaDY=@5p`z`jVXO?fnB}zVX|eo$Y<Yo67#5o4VK8-s*8f+^4(Np6y!y^Y@CpZ}h{1&i3Auqh!8VpIy%O{@Jxe-nID4!`l6Jo0cu|N$>7+wznd#i09!u7<yD|-{Qwi@mzuzq-f(g+)d=&?Gle^?XNWy&)fZL)l_GD*PR(+efYOMIH8TdPCKzq+!<j<we|@yVx8E_Drac()3xde(Y{RIV_N$&UBtTd_brv_Z0`=rNfYh;)lX>iGw#MwIiDx8wDBw%CDx&9_WpEje)dfi_hYxOpQDXuc&1PEQ`VK?Z0|X?PRy70NtV{$zqI24k*^kZ%Gur?&_Fy7|Gc5O+Is7nv|F@4*E&<{|J<@<@%^1tt-b5slSDDjUDves?u!Xuihc$M=V|>XP1_=#Z}NaF?R^>k)F#pXW*fbI^F^yf|G^%uy<H}Dp=iJC6|KFy`pyyJ=N3)U+IxnyUm$*Nej}~DU9{3#F|X?@>f@<%%`4h@?rZmJ-zv6M_^UkH{o32RB#8X`8?^S`yX$s{?{|Em&A;_=!cOsXtLy9Ye=cZ`$S1GSp07Q)^jG3}E?=oVU%Pzw10o;Y<D~Y!f7Seun2&|2+1h%z<Mj#ccUW7WcEm#Q-nw6`qpeSC#KTn4zF4v2+W52bj);83z*E}zA2m!9*MGG_nl}I2?uxv9q2EcZ|2d82J`r_Kdw;E|SLA-yv4-~k+F^f*@9hSk`?UA#Zy%?N>*gL$)7o!cC$8s>h&iCO&#oulbL(c<5p90lmbf4HZ@u<t^Yg+id7r%#d|Lb74dwfvd3%R8|5X-=yuI_rer<hrsU+stE}6bndtaW66nRgZ@ZI`)J}TR%pZG{?f9k%-d%LVmbhh_ZYayPueY^i;t^K_)k@q~m@Kde-PPWXSO;{=Jr)Qe%=kbiQ^z)wims>gWuKBypi1#kL_xmZ1ytnIPvA_6lJxq7D_eZ3QeZihmBSY)o*xyy&+}~B++}{K8OWWjX{TutfnfH#El&9U7Q4bW1$EXL)ysuZ*Y3;g3onYpz{<&wI?alh3p#T2u#pkClxMrbwYjvHo&VD?;7_r~`LVnQl_Vqn;#XK#(qW4p+^P12?`nO7-5&N+@Z=NL&#d~GWzuj=HcpuH@WnX9~o`>DNajJ7X-jw$8IZf%c*V*1RXOPHy#;!Z4t*gr&<>&RIsXncrx+_H9`_E8)9U|{4H8N3~pR6L{IeBunZ_?J!=KeBotn-4r=a<h!f3x4aB<^QxWielNg{|wge9>T$_Y9dA>&&~>Fxfu5dAycid_~r2rw_@x4*7t(5&3|+(a2j>9wa&Q0rjNHoAo5}{yM8=|2K<%>dXh!nQHtjMy~H<-(GDV%=%M})2u&L`&$h~-qo#DqO-j{;tyG8c8@&dY#&gss&Sh2s=99429dXB?cJr_@A61luWtV7u(N$YeXH7=^{whZ@usM6{SSloYxir`y=wknju3g@+<zR^?#rx)RsQYQWnB_f+Nbqz*2yZLk}T`wui0^DKLPc#%D=E$yw9GhF{xTVW?ikG`_~ubdwzRRy0#w7dRslmt{cVYvv*DWQEi=@b-0?JIk~b9-##xx>)));3+{J@tk3W7I_B&rpl(;=dAwTeH|{>OGPVBAdS1=Xq*~(V{ogG)p{+Nw&R5s{sin*(x6gL=6Hx!F@rP{{`;K=|i<8>?nCAj@-H{3MT(Bf6M_VW6c|qmlo|gNRdwqsBPV*e0=I8mMBJaN#oa^i-;C!L(D{ix>tE}_sr?mIQJa?#k$-j&D!LIp{)_=fxM2&NhCF(GDjs2P0Ix){Fs{Nj9aZd3ME0L#--#ovldH$-6sM`w83u-->=NdKtw;qc9*R{F7)_=fxM_qS$qB!rk`(Duc4>$*@@tk{6>`!*px3qo&&PS@Bm0QI5$Tu}8TkGFEH>r6x&rK?Sy_(3|7vI(I%REo1@uY0D#rmytU%xN&oTc(DhrA=cPmIy8Yo5PUzDAPByIXJ2uWO#mR6cR=$6|eDw$=ML&uc3G{ydqVSW>^Pd5%;0AFheK>$%JNb<OjgT0d3pioE|p6McP}=RTExw?eYW&ls=2cjkFewa=d|^4|DL+I0iYi7NljLYYs?(evi{QN5?bGGspch?WmHSE_u=BXXb4sj7cInCDG3KkaVGbJQoTw9mJIbEwMSKQHpW+aGB8fb*$Zw+s4;bDiCBnwAeZx2k-Zrefdqhwj(%0q0qjFS1bNJyEmuym`)5`K-ZW-?gu9*YW}9UzH#Afjs|y*XM|qH_ydtekO;@@5j#6^X7S3J(u7qV*j?^d#vZpbF}K`bch(YRW(Gb9|F$TDxXqTp7%}{IjHq-p1W1P?Iw|TFI}wX&GWeG-#m}2_VIIN`?~2`d;j_0MBeUoRc~*e-_?3H&+jT<DqgnVIXFpcKc=);m;P@%9dNb}IPa^xdEQs~e(PlWy3wC&?ahA&P}e<kP4=^BvEGmQ?*pp6`R@a&z4`A0s{OuRvi+qm)@kjHe>W(|k9$jgE`;sVuIrwEK;*sSwocQ=Kj^INXa1-9b-(#h=3|%3{@4GA&#SYiQ$&AXFHI>d|9$RuXM6vqrQ-bM-gRfUv%N26iO753n15L7-#p)`ym`JuKHz+(^5*$YUDrIXsd1X;FV&BE&Qjws&rK?Co}1Kl&2x~tu6YhZ-qWy>?8h#7RO|n>it_g&F~KLb{>^ic>c>3qARln9DR?f%`33oabBdZD^E{%)X`VaOc+B$!^4`u(<USNvJR_x$ygh0`j&{H1xkFvoJYT5so975M59WD6^>3aFR6l0@ulh0Td^LXdv6x@ahI`qC<$d{o=4tb0*8ggqn03C&oAtaJk6E{?yjh>C@tAeEx?i*2R^zPIFF}lFQ|H{2Lh|m0UC(Ii*{s9Wb<KKPwKwZ()xTLMtA5OSSoLGpy()ir(ubjij9=x=@dwny>bhp#tJ<6Ot;(Bqta^{kdR09yvo2M6v;I{5SKJ{!r_A-H@&W73tV`9pGV4$EUYK>J8oyajs{YNoQLQVpK2-N*)`9A}%dd;PwXLZ3eyP0q`4CVas=QeTs_UBdo*KVd*Qxn2>o?WjtkYE9tjAP8X5FRo7q5!E`T4K%=I4Jv-KFwo-KFNutfN%ktfSQPGV3DM-mHIA-mF_xKW2TR@@9Ra`Z4PhmH$um$+(GP9hmio%A56u|EnFj^7?u`Q;?^6CS3a~qAyG2HHv!PvM5SfA=cPP$Da^UlD?D{{wG8eTK%v7gy^NVFa3Z2glH-s!xSD>c+ilh(b9xY1y|!S9sYE9#4qrOgC7TvxH^v+@MpjycJY`6e-^yzV#@e23;rB<#EW>$WtO!NItSdI#~~gap{d}uJodrg2amWlkKOQh!y|r)M-u!bc*HGvY=gfI9&vLX@$lo}5jW+r1^yOz#Ep4ug1-qK@ryh*!ruswxB-uK@Ylg3uE%3F{MGP?>(KgvzY-pCEgs9^FNa55lgBdn%is~yU$d=%zXBd{T^_68uYy+_`T9K8AXYhY4SB3btU<034=+3~JmMxiHpAZxkGL6+t?;+PBW}SX0e%8J;#NEo;U~f)ewjxy{A75<ZFua3zZV{HJ01t%AAm>Pfrk&i4<2zR9!KFHg-7h>aRUAcc*I?JoPvJ}9`UO@a^UB{BksoIH2l->h`aO1ho29RIE=@)@V|ve+>6I0_?O@j_u+9B{#AIy;XJOxzYdSMKaZc_{{)YCAdlPdZ^I)V%;Q)1zrrIP%HwzVzr!OQ#^VwENAQLsKb*%C#3STJ@+iurNBRWqY#t?;^ht|?NAn0`(kCqej^Yu_q)!?I9?PRVlRjxMcs!2~CVkTK;0Zh`G3k?rfXDHuz@$%F2^`I%ER#NI1@IUirJ3|e%Yq|$lw#5+Ee#&Uqd1d3X({js9*jw!v^e;69)H6B6CQB{j|cD{z#|^Q<39ZR@Q4TTxC{R-ydlUB;BgCa7rA~sZos<%kGL<7Yw)kZBks-PGW^T%h<oz52>&8H;vPJ{f&UFW;@5bbg?|<vaaSIB@blmizrrI6eil69&OA=SKM9YR>VRYLkHI6RJt-A_Dm>!FJeFGW^Otlb_&s>bpv%D&E8xEeUIJYOUIKm}x(56{_(L8aLDxgqSpWX4_QL-NyaBoyyaD_PbSwB1@Mq8j@MqvJpo!owz}un8;O*d@(7oWD;62a-;632|P#<_dI0bqXoB}=qJpn!fJ`OzvJ`T=+=72N6+0fJAZ15RqKKKmy9Q0f8Iq(JOCGZ8XA9@w+2Y(N}4*nkeBlIWmkKlhnZ-f5@z61Rgd<T3F`aAd@_z&nK@E_pE&?n%>U<;qe^x116h>Jl>fQx~jf(C(~0zU%{20sHX2Q3dS2YwbB0)7_!9JCVnIdBzd1#lH`WoTJ&WpG7kX>dhw8E7eR8SvB4;^3#jC7}#l5?lmIpS?x!J@H?b)Cb_dzz?DK!4JW|LGOZp1OEcO1^xy6GxP@dXYftvHSkUF575itAHY|j7r|G+-$B0te+NDfJqtb${+dTFG!J?foCz-rng^yh2|p8@4m}1=2d7!`v-bl_e*UfmuZFG#uLiG!{u8_oyb<~_cq4cd^i%LA@D}Lj;4R>I=$GJl@HXfU@HTJ~bQd@Yyc_xzcsF<-^dNX2_z?6k_z*Z1ng&k8yrrUj2PS<|H<<cw$D~i%0Zij*!=z8z4ou^JnMt3t4Vdn?1(QDM%V3(HW=#5|Ex<INO_=man}KQm8!_pVHUZP~s?VfP+6YX~w=R=DX?-xQhuTc~q;<ixerhu5lhy{)-tA)2C#?yly}LS-KB)^#dv^^cebVY++PiBp>66v~)81W&NuRV9nD*{^O!}mCz_fQaVA3b82d2HdF_S)N12FB~O_}sb8-r=@ZqB4n+7wKCcS|OH(&k{=yIV8qlePrY-rbf-pR_fY_U`sf`lM~aw0DOx>65kx)85^gNuM+nOndh$O!}mq!L)aGWzr{o1x$I`zk4tl<WY|H?w(9~J>e14-rbu?pR^~K_U?X6`lP+VejWpu^hx`HY40Ayq)$2kOnY|(lRoJnFzwy1GwG8?fNAd@!K6?6I+*tEQB3-zBfzwGk73d$9R;SnJDN$KbPSmG?r}`|q|sp7yC*Q|Pe2=D%G3Tm88N|;qy2j-Vlr~HcgMhsfk#YxcP#u^c*L}K&wxJz9x?6RGvUvKM@)Nn9Q-(V#I$!$hd&)2G40*c;7@}`Ondhf_*38!)80J^{v>$Bw0Dn(KOP=2?cHPHkA+7}dv_H4D0sxQcaMfo8U?1kdnA)S>1Z(R-NTvmNk@Wd?;ggaPdXe-d-q@_ebQlI+Peob>5~oy)85^mNuP8enD*{)CVkTWVA{KTG3k?rgK6&$W6~$>1*W~bJCi<X7?}3%SDExlyMt+O>cXT?`YQOaCHJN@XcsW;OSA`dL=d-vwgHpA3?^*>ZUt@#Z3ZT70w!$)ZV0Xhtq&%x3nr}%t_H3OtqCS|fk~@_tAd}0)&P^%0+ZGOKM#HZS`SRx08H8#`~vtzXj3q0b1-R3@QdJ=psm5AZNa4N!7qV3K|{f$ox!B9fIER-gLVaz_5hRi1iuFE3+)Xi?FS|u0PYJO3LOL{jR2Fr4ju}QgpL4{jsla80Y`%0fJTE!$AL*FfZqVmhE4{PP6d<3fM<i}LSw<CGr*)X!E?cLpmAW*>0r`n;5pz~&?#WjNnq0P;91~_(6M0BC@|@0@I<i9<a<i*ryD`s1=<bV1^g<4xI2P44B7`A2JVF*4o498hYkVv2M<IL4@M9VgWBL>;Nb}3k<iiL|KguPZ(4F~&gMGPlIxn@oynXh@tDuUW67VRApRSVw|V@xCFk`YT;H+eGojy=ylctlxq$26Ex8tAxyD%XJ)6k&4NHDz(C=C1T5@jYaed2@_g$WAB_6>D;vfWZ2?TKw1hM)eE`}g}3PJn~g19V#I0RZ5{2cgMXeDq3XeC5><Vy1>XVEX)WDple5HkdEQ3P>G1o6`d;xdSG=)VH^SwuOEk+dSX4BC}P1Uvc(M&H4hM|G_rTt5hNs>V|SV=RIBRbwuK`zV6BX1GV@nEzsqdoPCh2=B>?gcSWx|INX_zdWKN=YM)&{-pk^P3KQ`<9!wUqBFc_aT+@xXc4jauDR*E{{bJJ3;6'

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
