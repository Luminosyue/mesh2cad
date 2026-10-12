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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/aa1a732d4fdc44e0a20cee312a929d77/part_009.stl', 'relative_path': 'aa1a732d4fdc44e0a20cee312a929d77/part_009.stl', 'source_sha256': 'd7e530f220e4b864aaf9b63fe0f074cae9e915a4fdbe42a1f32893ec61b4b2e2', 'input_faces': 376, 'input_vertices': 337, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21341155469417572, -0.18626345694065094, -0.35764652490615845], [-0.09926886856555939, 0.08549230545759201, 0.46996888518333435]]}
GEOMETRY_BASE85 = 'c$}r12XqzH+J+|yHFOA}U14ZRfKVi%g}@mgQVb<DrHCA)Tv3`N$Q1+!Feq100RgXy_lTeZ7D8_!6F?NChR_9$U?6l6NDvh7>~Ft&?tHWS*ZSB0v({ekJJ0O-X7}?kVoGvYkqAxxsjY>6nYgm5u4$r_)*`f*M@~!|J$z(plW`MX3DL?E7k`v4?AgCZ%D@oqWo>Hoh>@woCq^ge(TSs4N5|^XqsC86n>cLT(D4&Tj1;`{uraA4ZJzr4un8mW>zKH>R<U|qgIIl<{(t-vZZ{!Vq4y72LUS%`@Y(9`cV@Rxy+RG*X3lZRd)Jn{{P}&vvmUGw*TH^8za=eqg1B+GqpaUIo$6cVcFFpO+Y{IOv?FemTP^En{Yr7nKFP!bWoHo&WG~Jj-uF}D{<33<2eTItH~I{g@x#9TPH_L>1d4AxHJsXG4caXErPyuso=NMDWVv}t1IY((VcZ-XE&0!1F&_BvG2&XA9Xw9$YQ**GD;d{P!-)sJ%Vu0(Rg`!z_A~z8iZ{1Xye=ykw?51#9{6P^<Ho@gTV*^RM?a85-2C0*aaQb>aayn9yk<6WOUq<D_{(M)C-NKK-+dd28>crB_lIT3_8e|0=e>V58h>s68p(r~vuQjQ%*e@d^H=u~H~rffH@ht%9_)OZasQ=W!~@B-kGi@3cA-V}hjwG!Jhx2p)GLSF+}hBGc%a67&IjaW(Q})-F>X9}O7af}^Y+X;MBKk^1n<|hEXli%<vemFacgrL=ac3U4>X#}xSmx;)=!UQ?a|Ytc2K`+|8|hI|5|C{R^54r**NHTGO0anXEUw`bBP;sO~$Q;>xc)IzRKgQew(-%Glkb*)ORz*>2{N~KM>iJxR!g3acx)`;{LqLj9dDxO%$i)1->5oA0w{yJj2Il`!?cM@ETtaGjlf*Z*rD#ZGS)FdgmLg{aT|o#DkmfFdp1hhq%A~LtcM<MaegY9bx=@2^s%*X~qNjzi*&^EZW7|V;xH*9=!N(#*NoMT2J>kr7|9@cV`{(3bpvWq;({&M|EM`_<G%1damJQ-mk7bh#M8Y;`3-$ByOF*MBE5lA={sGn)Y>YK%U&!VeiQI?s`P$u=Uhy!~>yI<$HHMAg({vintm2l8m2|BjfaML|kt?TF%$h6Y{x7X*6z%YfUrddm6uz<K{-Sxw2i2Qx7v9+g`@oKk2BOTLnMvq4|3I;Xzja#b=2d9fsvH{=<=PDSl$&0XGlKiY9LKZhnllGdpcJwR8HGAKcvk?ebkz|9Ftq*FVYGN$pxZb03SJnn&lGK4#Q$HxF)nXvy`mY_FS}J?_bK=8sHX|JNdP4roW~viiaBoAP(<>x-<u+4Aldx<9)ltMBi5miCwa=5bcvx^tb@t(D)8)z=19k?X2d5!NsNymo7-e%ojk#~AzgSM=VN<=D6x({Hb&cCCGjk8@ho=cFCR>}T!iKW#a^r|&*Kj}4z(M)kia%jf;`lmNwFb(O6X^V20u>3(wFA;uG8KBViUdu$z=u?OC#_om*F>o#<VjGsMGuK$50_Xzbb?jYM4v4_@!mVBJzD6VC-Anva+?x>ramCw*R(Zk0cV)ak_CVw|SNIl5v_qa~$MDMiv0INUx6<R08jp~dCr#Gf`Vm7~<%j&;aR{ma`lKGF~dPGV2d(rEA#)D=4+%DJuLdLE2H;G#nE--G)zd>BP^!<KTKmLs5FHGU_D`yioDn8(G&Mzk(ST&q+zc!P&-mx4X=gvcj2elMle_)(!e@tywU%y{m#)&dmeeIc(GJnf#!s?sGdy>yDeT>x)Pm}rK`c}ODlnyeVOl-o(?PHlY`rm5H>o1e}o^dIbkI$Zf%->ohu=+-;aWa3)Y{uhjJ!Kx4wTX}a_BO<WOXFA^e_lz+*R|o}-|aM=8)kA0ALsn9x5)clc>Ra36SpQ*W%YxGU&d)VkgvDr+7Z{jE5gU2QElS>q2pM6vvhIdf#Ns$e66`l`G)l<jLnNV_YU#k(Aj)F#9fs6%$;1`{>G<d-cl#P>mNTV`TJXWdv>nhB=<!=8)xI>^D<9(c$)1yYeHL@Ckz?L_Nf&gPWgbDw}90T^nO6+t$DpDI|qz~H#3MYZ^G&uk+F0R2d-!EbLN*7@*G}Xn{gxU!fLusnI*?RBwEf(_6zuZ?<IfV_dG$rqu%pGaqoGexc5A9;&{#z#l7c-;@)$^sqZ--6!-3Tr=6aCt+;nzJM}&L+Ntl^*G@Y<``YQRXa73w_v~LMj%WWm{qpQnr=6bt=#0N-e>wF%`^Aax*%wYbJ^R9`@7Wj5_;~h((=X5ZSKPbKo%edyvlHL5o}K!h^=v*|EAzSS3H1FTFyJ1oXXD{=;{NUJiE9H^%XR)+bK+L^2ekhE11r(*yYX8c;=$~X<-QoOSLVZ)%1~bD&2JU==C_J_^IL~|@>|8d`K?pmlixbrliw=t&2OD{dh%Pvz4@)vUr&DP#P{U4ihJ{0#l88hQ{R){I^2`rI_>oA3n#uO?{)g?*)L8UPd@C7zb7AdxMw{(<KS7(&U-!iv-4h0{_M=7Cx3RhCx3S0d-7+eou2&JiQ~zi9q!4Wo$>VK&kpzG&kpzG&(_VEv~J9Uy++W!y4U+G?Z2CSh-)95oJ95SJ<Yft7m@B`JcY&43uX{EZqy@g{ByuW(t<Y_*BkYl<#X}i_42$u1q+G$uV0nlv;Jr{j@nc3KI2CH^)q}fZe81x{a5X=uI-j_X3c$*=JDQW#?AOa^L;MvzxEk%Yf|@g`QF8x4^Df>$M|v?=VG(xWq;Ed57vw~eJ&ojIz`4A9Xpe>;4{X}l(e}%7q_l-lsxm~bQym><5tppb9{^^vT+F97;uKh<4SeLRr|Fo<+I)MW!`x9jGL?ZQaqSnOpfQ2o!zN^!N1PBdGN9P$vzhk<o`<Nj@kG4yR!YWIPZLQk<Z2b`B&vRwP?&dIX+)AZnodI(C6ZMelBri_Lw=;uEMR1>n-=u{3@>H@3-9JpcPD$?Z5oJ<z8=rf&k}HxwPICw=Qp&{EHHG={*InF>X}IPxHCBd3lYjKl#ga*{@F-*N5c3<8$%grMa^Hk!Hi?xV_G}8J|DR=i=t2agr~sI$5^=OUAAE_31tr4@?|R-22_$;hyjIihIA?EAIVn@5J$Zw^!Wz-Cl9;cYEi(p6~XGd%xQ&?)`4>#P@u+cj9=y+dJIz-Cl9;cYCM5p6~X-yw0-ykD85_>tvpsNAN)XyEA+)uH}`N?|t|BTNJPGDCY^`wEq9gOG};-Mf*!H+{d_?ltBAS@!-!z<oKJ{-;n!d3*+X>_h0!dZX`s!;rk1&#f8szbN}Ak@;m#$Q48ccU&gr6W6Bbri|c!@NIvJ}OVnSS=ZXg!M$q}AcwkS5EcbY-IEt(BRNUCpBFnumw8A}%t9_xkfA@wR?tK?1Sk1WFcZwUkGj_Q5wNZG8akZ}%*LE)@uFk7K;Wft9d8K$@*9;k7{SFr9aE^0Hac$QS`QImSewu}OjH~lg@!-z>G7io$t004Mb&e_S-`PUO!TA|1SSQ<)T~x+VzYB$@7<Yabz|HIs8Atst6lQa-eiy*C?6aBf_XY}ol<~9XNsiw~f8kGztKUb(tsOli$M0{jP&?=5>i1W1Ju^>!Uqe2i-~Zz*<H!dTx3=$<fA2*;U=`kAT;&6b2ezeeXX9CTTaNR#m$tj--MC-&oSUosNAcj+fwDgG95p_Qt2{?>eQSO8UjO|{6vx<dMV{{}f4g6XaVLKR4{n;jjmN1-+}w!2pCg}C{Z(A$lZtB_&Ti%7a97q}pSjgN&c>}=%0mKcvbVU~Y2Esnan(-6jc-P8VexNWIpa%V|Egf+ncP41iuR*+DXB$hqlUTuNr8akkJ7*XCk3P9|9AhSpjFHN?>{L>4AHbsc4-go3V+RR+XcH^hMtEPbvmP-&~ETI?Rz1%UWY!=q!&f_eCU06@s20#(hS-PUc^d98<KHP_%3#N67Lh*9lohuTH2)@Gzq@Ye#bq#R11+>D@1zHj~~$&p?UB@yPUPlIp`U9(cS{IS?DGBW@vMDs17gsST#gGR~1b7KkRbXE@2^3|Ag;`zI25q!?#0Ux<H?V7k#LOe%C^ug};ox6hiO8pF>~HLw|(NM_+=_v+&i?7tv;+1sH?JY#(Kpn$U*uVr~3{m_Olt!Z)$+wXjP9)PQeomw3B$fcoGY+oir;+CUq?|IIE%>{0`&!T)aCJ9fDNy#oIW#`$OHRd_M}MX^qWhQNz{R7GEekHvKY+MEdO1n<MT?*QKs*KN?|w$MiKHPGfN(BCxaMSHKI%~!C;uA!}0F_uCv!i(`2?XCljgcs|j7xszJ9`Is5f5n^&y#+7USPGs?!86GiTQSy^p|#<~y6cIx*%Qxn#~g_{s|$^W7xVH6b0U0bh`bhSK&*-8&=~kzSd(Ya#@o1Vjdc?TZ4TcA>n{dc4_>@W^dS^|sSGdL@eu3c4%#NJ<FOVWhsME+u@!425*miF-eCLTcG(DB0>9ZVNp{%;?Et?Kbv8qj;7f>e!7d%4o#4Yn`*FVr?v=njQKuNRID9cYqn=fDL-2f2XmR)?#0-HJfiH?WOQ4<Lm%t}MtHOuknc>hS@EYQUy5fdnEX0^>fDU*0Bs`adXEbol6*CmR7}^&GEdpQ3E*0!j8AbRi(6aDV;3J`>;UnQApyBXBOTtIMSA>>=uLxfrS_Zy6d^zFmPF1u^S!e`&S@=@WO7NxNOF}EamxM2lB78AuIe4LE;ETbRfR=_Y0Us{*wcWlQcIgV;4&N2NGjuC_XZR<eTi~C7?*iQh-vz!KG!s7AE+T*G0nLW*0pAO{3%<8qzO_qV=y&ja;rm1P!S{!M8hQZ!Y4`!q!|(&(2SIb-2f;rB&4qsk{#od8_-En$(39}b+2yodhCxrk4}%{HJpn%yehBm!{1EuT(4+8!;RiyGz&~Y|{dVaG{T{v_d>`l@_&)F{(B1GU@I9eB;d{b&hg$I6;h%)=fInoHgLcV)u7Upn_f|qP;P>L*7todP|FFvocKHPQKKuf^%);}tP+$0Wac>PY1O6?$%(Kgv(68a=;2o=>pTJMF%LKc83|$KUHs0|KbPc?SITvw-eg!`b?^pp{4KHGjMO>jD!oP-hd=C8vUetLJ^@RQlemtJ}2>LnvB)d$u%fF!kc=7BQJTLSE_$i3>DfA<F@$4&jUg$FT_v|v;E^DEy;1}WEI_O$>@$6JQFLXJ)n7bL6zZsZw;TI#;dgwa%sTkAc&=v6F+39#*=x6XF?J~kHHK5hu(=f*kpfT{GJ!0L&LlfcW;C;=Zjp5(Hy*Oxd_?PUGYL~judhlXx{L?P2p{?NOBUT$|9DFL~vL3WPym<BvJTJ5*{6fS^fVP1jk2#Kp#=?)ry(nljyoi~OxI$aNzlV3Ug(kp@wKPr>e;t-u2mX1yLx)Der(>*JK;z+O;~kGf+rp2-nAU;Th5tL=Q46ZWkHWp0&|2_f?o7;|&?fK`@k|V~CVX9tcMa&@T)sZ8g+2z~7%`he<6OQeuA5?Bly8RXW*AT9AIJ6M7zg27W1bDD&*fX<T4;NhZ-Hx}?OZ+{*FqEF#ky#u$#oD79|dg)9|f;N8^AZfI4d86>llou@U<~-)u7c~zAmooVvL0sYxPx4=2t??!@q8qnVQT2g;s)pQ<H0`3bZo3*zYfEGFN*UF@zWAu$cQ&&@%91pNca*5?Tdb>_@TwN<+ipC*fXMXlZzH-ioukB(xN~*k57~M?fRtQ<6hMBf|ct|7GRBe@sfC-TwoN_euU)%KhY1b}Z*3RZ4PEk!#zDcPMozL#$TqKkH|Iwg'

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
